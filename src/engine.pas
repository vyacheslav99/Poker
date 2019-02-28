unit engine;

interface

uses
  Windows, Forms, SysUtils, Classes, Controls, Registry, ShellAPI, IniFiles, ShlObj, ActiveX, ComObj,
  Variants, Math, Graphics, MemTableDataEh, Db, MemTableEh, ExtCtrls, utils;

type
  TMsgLabel = (lDeal, lInfo, lP1Order, lP1Take, lP2Order, lP2Take, lP3Order, lP3Take);
  // каллбэк-функции для вывода игровых сообщений, задания конфигурации доступных эл-тов управления и отрисовки
  TDrawProc = procedure(Full: boolean) of object;
  TSetProc = procedure(SetType: integer) of object;
  TSetMessageProc = procedure(Target: TMsgLabel; Text: string; Delay: integer; CanClearAll: boolean; ShowMsgBox: boolean) of object;

  // параметры поведения игроков и уровни сложности
  //TDifficulty = (dfVeryEasy, dfEasy, dfNormal, dfHard, dfVeryHard, dfSharper);
  TDifficulty = (dfEasy, dfNormal, dfHard, dfUndefined);
  TPlayerBehavior = (ubNormal, ubRisky, ubCareful);
  TPlayerPlayStyle = (psForSelf, psAgainstOther, psMiddle);
  TPlayerControlType = (ctRobot, ctHumanLocal, ctHumanRemote);

  // параметры игры
  TGameType = (gtLocal, gtServer, gtClient);
  TGameOption = (goAsc, goDesc, goEven, goNotEven, goNoTrump, goDark, goGold, goMizer, goBrow);
  TGameOptions = set of TGameOption;
  TSpecDeal = (dNormal, dNoTrump, dDark, dGold, dMizer, dBrow);
  TJokerAction = (jaCard, jaByMax, jaByMin);
    
  // колоды, карты, масти
  TDeckType = (dtRussian, dtSolitaire, dtSlav, dtSouvenir, dtEnglish);
  TDeckSize = (dsz36, dsz54);
  TLearName = (lnHearts, lnDiamonds, lnClubs, lnSpades, lnNone);
  TCard = (
    ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, chJack, chQueen, chKing, chAce,
    cd2, cd3, cd4, cd5, cd6, cd7, cd8, cd9, cd10, cdJack, cdQueen, cdKing, cdAce,
    cc2, cc3, cc4, cc5, cc6, cc7, cc8, cc9, cc10, ccJack, ccQueen, ccKing, ccAce,
    cs2, cs3, cs4, cs5, cs6, cs7, cs8, cs9, cs10, csJack, csQueen, csKing, csAce,
    cJoker1, cJoker2);
  TCards = array of TCard;
  TCardSet = set of TCard;
  TCardsObj = array of TImage;

  // сортировки
  TLearOrder = array[0..3] of TLearName;
  TSortDirection = (sdNone, sdAsc, sdDesc);

  // ИИ
  TAiAction = (aiaTake, aiaPass, aiaLure, aiaWaste);
  TAiResult = (airTake, airPass, airUnknown);

  // игровой стол (куда выкладываем карты при ходе)
  TTable = record
    Card: TCard;
    Player: integer;
    JokerAction: TJokerAction;
    JokerCard: TCard;
  end;
  TTableCards = array of TTable;

  // игрок и его параметры, список игроков 
  TPlayer = record
    // параметры
    Id: string[16];
    Name: string[255];
    FaceFile: string[255];
    Password: string[255];
    Difficulty: TDifficulty;
    Behavior: TPlayerBehavior;
    PlayStyle: TPlayerPlayStyle;
    Control: TPlayerControlType;
    // статистика
    cAll: integer;           // +1 при старте игры (StartGame)
    cCompleted: integer;     // +1 в конце игры
    cInterrupted: integer;   // +1 при прерывании игры (StopGame без флага Normal)
    cWinned: integer;        // +1 в конце игры, если у игрока больше всего очков (он победил)
    cFailed: integer;        // +1 в конце игры, если у игрока не больше всего очков (проиграл)
    cScores: integer;        // +расчитанный выигрыш в конце игры
    cTotal: integer;         // +<сумма очков партии> в конце игры
  end;
  TPlayerList = array of TPlayer;

  // участик партии и партия
  TPartyPlayer = record
    Index: integer;             // игрок (индекс в массиве игроков)
    Order: integer;             // заказ в текущем кругу
    Take: integer;              // взято в текущем кругу
    Scores: integer;            // очки в текущем кругу
    Total: integer;             // общий счет на текущий момент
    Cards: TCards;              // карты на руках
    OrderCards: TCards;         // карты, на которые сделан заказ
  end;
  TParty = array[0..2] of TPartyPlayer;

  // раздача
  TDeal = record
    Player: integer;
    CardCount: integer;
    Deal: TSpecDeal;
  end;
  TDeals = array of TDeal;

  // масть (используется в настройках и для отрисовки мастей в графическом движке)
  TLear = class
    LearName: string;
    Lear: TLearName;
    Icon: TIcon;
    constructor Create(ALear: TLearName; AIcon: TIcon);
    destructor Destroy; override;
  end;
  TLearList = array[0..3] of TLear;

  // вышедшие карты
  TReleasedCard = record
    Player: integer;
    Card: TCard;
  end;
  TReleasedCards = array of TReleasedCard;

  // вышедшие масти
  TReleasedLear = record
    Player: integer;
    Lear: TLearName;
  end;
  TReleasedLears = array of TReleasedLear;

  // ********** Типы для сэйва и файла игроков ************
  // заголовок файла игроков 
  TPlayerDataFileHeader = packed record
    pCount: integer;
  end;

  // заголовок файла сохранений
  TSaveFileHeader = packed record
    GameTime: TTime;                // время игры
    szDeals: integer;               // размер массива FDeals
    szStatTable: integer;           // размер текста, в который конвертируется при записи содержимое таблицы
    szTable: integer;               // кол-во карт на столе
    szReleasedCards: integer;       // размер массива вышедших карт
    szReleasedLears: integer;       // размер массива вышедших мастей
  end;

  // параметры игры
  TSaveFileData = packed record
    // состояние игры
    CurrDealNo: integer;
    CurrPlayer: integer;
    Trump: TLearName;
    CurrStep: integer;
    Bet: boolean;
    CanNextDeal: boolean;
    CanStopGame: boolean;
    OldStep: integer;
    NoWalk: boolean;
    TakePlayer: integer;
    noPause: boolean;
    // опции игры
    Deck: TDeckSize;
    GameOptions: TGameOptions;
    NoJoker: boolean;
    StrongJoker: boolean;
    JokerMajorLear: boolean;
    JokerMinorLear: boolean;
    MultDark: integer;
    MultBrow: integer;
    PassPoints: integer;
    LongGame: boolean;
    CanPause: boolean;
    PenaltyMode: integer;
  end;

  // игрок
  TSaveFilePartyPlayer = packed record
    Id: string[16];             // игрок
    Order: integer;             // заказ в текущем кругу
    Take: integer;              // взято в текущем кругу
    Scores: integer;            // очки в текущем кругу
    Total: integer;             // общий счет на текущий момент
    szCards: integer;           // размер массива карт на руках
    szOrderCards: integer;      // размер массива карт, на которые сделан заказ
  end;
  // *********************************************************

  // игровой движок
  TCustomGame = class
  protected
    FStarted: boolean;
    FDrawProc: TDrawProc;           // процедура отрисовки объектов, нужно вызывать после каждого изменения
    FSetPlayerConProc: TSetProc;    // процедура установки эл-тов управления пользователя
    FSetMsgProc: TSetMessageProc;   // процедура установки сообщений
    FGameType: TGameType;           // тип игры: локальная, по сети - сервер, по сети - клиент
    //--- параметры игры
    FDeals: TDeals;                 // массив раздач
    StatTable: TMemTableEh;         // таблица игры
    DeckSz: integer;                // размер колоды (реальный)
    FCurrDealNo: integer;           // № текущей раздачи (индекс в массиве раздач)
    FTable: TTableCards;            // карты на столе
    FCurrPlayer: integer;           // игрок, чей сейчас ход (индекс в массиве Party)
    FTrump: TLearName;              // козырная масть
    FCurrStep: integer;             // № шага в круге (шаг - это действие одного игрока, всего шагов 3)
    FBet: boolean;                  // какое сейчас действие - делаются ставки (true) или ходы (false)
    CanNextDeal: boolean;           // флаг, что нужно перейти к следующей раздаче в процедуре Next
    FCanStopGame: boolean;          // флаг, что следующим ходом игра закрывается
    OldStep: integer;               // предыдущий шаг
    FNoWalk: boolean;               // запрет ходить картой
    TakePlayer: integer;            // кто побил последним
    FLearOrder: TLearOrder;         // порядок расположения мастей
    FSortDirect: TSortDirection;    // сортировка карт (нет, по возрастанию, по убыванию)
    FReleasedCards: TReleasedCards; // массив вышедших карт
    FReleasedLears: TReleasedLears; // массив вышедших мастей
    noPause: boolean;
    prevDeal: TSpecDeal;
    //*** property
    function GetPlayer(pIndex: integer): TPlayer;
    function GetCurrDeal: TDeal;
    procedure SetLearOrder(Value: TLearOrder);
    procedure SetSortDirect(Value: TSortDirection);
    //--- property
    procedure InitializeGameData(CanFreeParty: boolean);
    procedure InitPlayers;
    function GetNextIndex(CurrIndex: integer): integer;
    procedure FillDeals;
    procedure DealCards;
    function GenerateTrump(cFrom, cTo: integer): TLearName;
    function GetCurrId: integer;
    procedure CopyStat(RecId: integer; ShowTotal: boolean = false);
    procedure FillStatTable;
    function DealToStr(d: TDeal; Full: boolean = false): string;
    procedure CalcStatistic(CanSkip: boolean = false);
    procedure EndGame;
    procedure EndRound;
    procedure DelCard(pIdx, CardIndex: integer);
    procedure DelOrderCard(pIdx, CardIndex: integer);
    procedure SortPlayerCards(pIdx: integer);
    function StartLearCardOrd(Lear: TLearName): integer;
    function EndLearCardOrd(Lear: TLearName): integer;
    procedure AddReleasedCard(Card: TCard; pIdx: integer);
    procedure AddReleasedLear(Lear: TLearName; pIdx: integer);
    function IsLearEnded(Lear: TLearName): boolean;
    //*** методы поиска
    // поиск карт у игрока
    function IndexOfCard(Card: TCard; Cards: TCards; Offset: integer = 0): integer;
    function FindCard(Card: TCard; Cards: TCards; Offset: integer = 0): boolean; overload;
    function FindCard(Card: TCard; Lear: TLearName; Cards: TCards; Offset: integer = 0): boolean; overload;
    function IndexOfCardLear(Lear: TLearName; Cards: TCards): integer;
    function FindCardLear(Lear: TLearName; Cards: TCards): boolean; overload;
    function FindCardLear(Lear: TLearName; Cards: TCards; ExCard: TCard): boolean; overload;
    function CountCards(Lear: TLearName; Cards: TCards; ExCard: TCard): integer; overload;
    function CountCards(Lear: TLearName; Cards: TCards): integer; overload;
    function GetMaxCardIndex(Lear: TLearName; Cards: TCards): integer;
    function GetMinCardIndex(Lear: TLearName; Cards: TCards): integer;
    function GetMaxCard(Lear: TLearName; Cards: TCards): TCard;
    function GetMinCard(Lear: TLearName; Cards: TCards): TCard;
    function GetNextCardIndex(Cards: TCards; CurrCard: TCard; OrderBy: integer): integer;
    function GetPrevCardIndex(Cards: TCards; CurrCard: TCard; OrderBy: integer): integer;
    function GetNextCard(Cards: TCards; CurrCard: TCard; OrderBy: integer): TCard;
    function GetPrevCard(Cards: TCards; CurrCard: TCard; OrderBy: integer): TCard;
    // поиск для массивов вышедших карт и мастей
    function IndexOfReleasedLear(Lear: TLearName; pIdx: integer): integer;
    function FindReleasedLear(Lear: TLearName; pIdx: integer): boolean;
    function IndexOfReleasedCard(Card: TCard; pIdx: integer): integer; overload;
    function FindReleasedCard(Card: TCard; pIdx: integer): boolean; overload;
    function IndexOfReleasedCard(Card: TCard): integer; overload;
    function FindReleasedCard(Card: TCard): boolean; overload;
    //--- методы поиска
    //*** методы ИИ
    // первоначальный анализ карт игроков
    function AIGtdTake(pIdx: integer; Card: TCard): boolean;
    function AICanTake(pIdx: integer; Card: TCard): boolean;
    function AIGtdPass(pIdx: integer; Card: TCard): boolean;
    function AICanPass(pIdx: integer; Card: TCard): boolean;
    function AINeedTake(pIdx: integer): boolean;
    function AINeedPass(pIdx: integer): boolean;
    // промежуточный анализ ситуации - рассчет гарантированных показателей
    function AICheckToTake(Card: TCard): TAiResult;
   // function AICheckToPass(Card: TCard): TAiResult;
    function AICheckToLure(Card: TCard): boolean;
    function AIIsBeat(Card: TCard): boolean;
    // окончательный анализ ситуации - рассчет вероятностных показателей и принятие решения
    function AIAnalyseCard(Card: TCard; AiActn: TAiAction): boolean;
    // основные функции рассчета действий
    function AICalcOrder: integer;
    function AICalcWalk(var JokerAction: TJokerAction; var JokerCard: TCard): integer;
    function AICalcBeat(var JokerAction: TJokerAction; var JokerCard: TCard; Rand: boolean = false): integer;
    procedure SetGameType(const Value: TGameType);
    //--- методы ИИ
  public
    DataDir: string;
    Players: TPlayerList;  // все доступные!, а не только участники игры
    //--- опции игры
    Deck: TDeckSize;
    GameOptions: TGameOptions;
    NoJoker: boolean;
    StrongJoker: boolean;
    JokerMajorLear: boolean;
    JokerMinorLear: boolean;
    MultDark: integer;
    MultBrow: integer;
    PassPoints: integer;
    WaitDelay: integer;
    LongGame: boolean;
    KeepLog: boolean;
    PenaltyMode: integer;
    SaveEachStep: boolean;
    //--- параметры игры
    Party: TParty;  // участники игры
    CanPause: boolean;
    GameTime: TTime;
    constructor Create(AStatTbl: TMemTableEh; ADrawProc: TDrawProc; ASetProc: TSetProc; ASetMsgProc: TSetMessageProc);
    destructor Destroy; override;
    function LoadPlayers: boolean;
    function SavePlayers: boolean;
    procedure ClearParty;
    function CardToStr(c: TCard; AddLear: boolean = true; Short: boolean = false): string;
    function LearToStr(l: TLearName; NoTrumpStr: string; Short: boolean = false): string;
    function ChangeCardLear(Card: TCard; Lear: TLearName): TCard;
    function ChangeCardLearNoTable(Card: TCard): TCard;
    function ChangeCardLearToTable(Card: TCard): TCard;
    function JokerActionToStr(JokerAction: TJokerAction; JokerCard: TCard): string;
    function GetCardLear(Card: TCard): TLearName;

    function LoadGame(PlayerId: string): boolean;
    procedure SaveGame;
    procedure StartGame(Interrupted: boolean = false);
    procedure StopGame(Normal: boolean);
    procedure HoldGame;
    function DoWalk(pIdx, CardIndex: integer; JokerAction: TJokerAction; JokerCard: TCard; var Err: string): boolean;
    function DoBeat(pIdx, CardIndex: integer; JokerAction: TJokerAction; JokerCard: TCard; var Err: string): boolean;
    function MakeOrder(pIdx, Order: integer; var Err: string): boolean;
    procedure GiveWalk(CanNextStep: boolean = true);
    procedure Next(canRefresh: boolean = true);
    procedure SkipDeal;

    property Started: boolean read FStarted;
    property Player[Index: integer]: TPlayer read GetPlayer;
    property Trump: TLearName read FTrump;
    property CurrPlayer: integer read FCurrPlayer;
    property CurrDeal: TDeal read GetCurrDeal;
    property CurrStep: integer read FCurrStep;
    property IsBet: boolean read FBet write FBet;
    property TableCards: TTableCards read FTable;
    property NoWalk: boolean read FNoWalk;
    property CanStopGame: boolean read FCanStopGame;
    property LearOrder: TLearOrder read FLearOrder write SetLearOrder;
    property SortDirect: TSortDirection read FSortDirect write SetSortDirect;
    property GameType: TGameType read FGameType write SetGameType;
  end;

function FindPlayerByName(PlayerName: string; Players: TPlayerList): integer;
function FindPlayerById(PlayerId: string; Players: TPlayerList): integer;
function DifficultyAsString(Difficulty: TDifficulty; UndefinedString: string = ''): string;

implementation

uses network;

function FindPlayerByName(PlayerName: string; Players: TPlayerList): integer;
var
  i: integer;

begin
  result := -1;
  if (PlayerName = '') then exit;

  for i := 0 to Length(Players) - 1 do
    if AnsiLowerCase(PlayerName) = AnsiLowerCase(Players[i].Name) then
    begin
      result := i;
      exit;
    end;
end;

function FindPlayerById(PlayerId: string; Players: TPlayerList): integer;
var
  i: integer;

begin
  result := -1;
  if (PlayerId = '') then exit;

  for i := 0 to Length(Players) - 1 do
    if AnsiLowerCase(PlayerId) = AnsiLowerCase(Players[i].Id) then
    begin
      result := i;
      exit;
    end;
end;

function DifficultyAsString(Difficulty: TDifficulty; UndefinedString: string = ''): string;
begin
  case Difficulty of
    dfEasy: result := 'Новичок';
    dfNormal: result := 'Опытный';
    dfHard: result := 'Профессионал';
    dfUndefined: result := UndefinedString;
    else result := '';
  end;
end;

{ TLear }

constructor TLear.Create(ALear: TLearName; AIcon: TIcon);
begin
  Icon := TIcon.Create;
  Icon.Assign(AIcon);
  Lear := ALear;
  case Lear of
    lnHearts: LearName := 'Червы';
    lnDiamonds: LearName := 'Бубны';
    lnClubs: LearName := 'Крести';
    lnSpades: LearName := 'Пики';
  end;
end;

destructor TLear.Destroy;
begin
  Icon.Free;
  inherited Destroy;
end;

{ TCustomGame }

procedure TCustomGame.AddReleasedCard(Card: TCard; pIdx: integer);
var
  i: integer;

begin
  if not FindReleasedCard(Card, pIdx) then
  begin
    SetLength(FReleasedCards, Length(FReleasedCards) + 1);
    FReleasedCards[High(FReleasedCards)].Player := pIdx;
    FReleasedCards[High(FReleasedCards)].Card := Card;
  end;

  // проверить по вышедшим картам, если масть закончилась, то записать ее в массив вышедших мастей всем игрокам, у кого ее там нет
  if IsLearEnded(GetCardLear(Card)) then
    for i := 0 to Length(Party) - 1 do AddReleasedLear(GetCardLear(Card), i);
end;

procedure TCustomGame.AddReleasedLear(Lear: TLearName; pIdx: integer);
begin
  if (not FindReleasedLear(Lear, pIdx)) then
  begin
    SetLength(FReleasedLears, Length(FReleasedLears) + 1);
    FReleasedLears[High(FReleasedLears)].Player := pIdx;
    FReleasedLears[High(FReleasedLears)].Lear := Lear;
  end;
end;

function TCustomGame.AIAnalyseCard(Card: TCard; AiActn: TAiAction): boolean;
var
 i, pl: integer;
 r: TAiResult;
 
begin
  // анализ карты - сделаешь ты ей нужное действие или нет
  case AiActn of
    aiaTake: // эта карта берет
    begin
      r := AICheckToTake(Card);
      result := r = airTake;
      if r <> airUnknown then exit;
    end;
    aiaPass: // эта карта не берет
    begin
      r := AICheckToTake(Card);
      result := r = airPass;
      if r <> airUnknown then exit;
    end;
    aiaLure: // эта карта прикрывает и есть то от чего прикрывать
    begin
      result := AICheckToLure(Card);
      exit;
    end;
    aiaWaste: // эта карта бесполезная (не берет и не прикрывает)
    begin
      result := (AICheckToTake(Card) = airPass) and (not AICheckToLure(Card));
      if result then exit;
      if AICheckToTake(Card) = airTake then exit;
    end;
  end;

  // углубленный анализ игроков
  pl := FCurrPlayer;
  for i := FCurrStep + 1 to 2 do
  begin
    pl := GetNextIndex(pl);
    case AiActn of
      aiaTake: result := (AIGtdPass(pl, Card) or (AICanPass(pl, Card) and AINeedPass(pl))) or
        (not (AIGtdTake(pl, Card) or (AICanTake(pl, Card) and AINeedTake(pl))));
      aiaPass: result := (AIGtdTake(pl, Card) or (AICanTake(pl, Card) and AINeedTake(pl))) or
        (not (AIGtdPass(pl, Card) or (AICanPass(pl, Card) and AINeedPass(pl))));
      aiaLure: ;
      aiaWaste: result := (AIGtdTake(pl, Card) or (AICanTake(pl, Card) and AINeedTake(pl))) or
        (not (AIGtdPass(pl, Card) or (AICanPass(pl, Card) and AINeedPass(pl))));
    end;
    if not result then break;
  end;
end;

function TCustomGame.AICalcBeat(var JokerAction: TJokerAction; var JokerCard: TCard; Rand: boolean): integer;
var
  tl: TLearName;
  
begin
  // ИИ. рассчет боя
  if Party[FCurrPlayer].Take < 0 then Party[FCurrPlayer].Take := 0;
  result := -1;
  if Length(Party[FCurrPlayer].Cards) <= 0 then exit;

  if FTable[0].Card in [cJoker1, cJoker2] then
    tl := GetCardLear(FTable[0].JokerCard)
  else
    tl := GetCardLear(FTable[0].Card);

  if AINeedTake(FCurrPlayer) then
  begin
    // если еще не взял свое или перебрал или золотая, то перебираем карты выбранной масти,
    // бьем первой из найденных, что бьет 100% в данной ситуации
    if FDeals[FCurrDealNo].Deal = dGold then
    begin
      // для золотой идем по возрастанию, от самых мелких, т.к. тут нет риска взять не на то, на что рассчитывал
      result := GetMinCardIndex(tl, Party[FCurrPlayer].Cards);
      while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaTake)) do
        result := GetNextCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);
    end else
    begin
      // в остальных идем по убыванию, от самых крупных, т.к. тут есть риск взять лишнее и перебрать
      result := GetMaxCardIndex(tl, Party[FCurrPlayer].Cards);
      while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaTake)) do
        result := GetPrevCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);
    end;

    // если ничего не бьет - придется скинуть самую мелкую этой масти
    if result = -1 then result := GetMinCardIndex(tl, Party[FCurrPlayer].Cards);

    // выбранной масти нет - ищем козырь по такой же точно логике
    if (result = -1) then
    begin
      if FDeals[FCurrDealNo].Deal = dGold then
      begin
        result := GetMinCardIndex(FTrump, Party[FCurrPlayer].Cards);
        while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaTake)) do
          result := GetNextCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);
      end else
      begin
        result := GetMaxCardIndex(FTrump, Party[FCurrPlayer].Cards);
        while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaTake)) do
          result := GetPrevCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);
      end;

      // если бьющего козыря не нашли - надо бить джокером
      if (result = -1) then
      begin
        result := IndexOfCard(cJoker1, Party[FCurrPlayer].Cards);
        if (result = -1) then result := IndexOfCard(cJoker2, Party[FCurrPlayer].Cards);

        if result > -1 then
        begin
          JokerAction := jaCard;
          if StrongJoker or (FTrump = lnNone) then JokerCard := ChangeCardLear(chAce, tl)
          else JokerCard := ChangeCardLear(chAce, FTrump);
          if (not AIAnalyseCard(JokerCard, aiaTake)) then result := -1;
        end;
      end;

      // если джокера нет и бьющего козыря не нашли (здесь мы точно знаем, что наш самый крупный козырь будет перебит:
      // следующий игрок точно походит козырем, т.к. у него вышла эта масть - надо кинуть самый мелкий козырь
      if (result = -1) then result := GetMinCardIndex(FTrump, Party[FCurrPlayer].Cards);
    end;

    // если нет ни этой масти ни козыря - то надо скинуть какую-либо ненужную карту. Перебираем все карты в порядке возрастания
    if (result = -1) then
    begin
      result := IndexOfCard(ch2, Party[FCurrPlayer].Cards);
      if result = -1 then
        result := GetNextCardIndex(Party[FCurrPlayer].Cards, ch2, 1);
      while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaWaste)) do
        result := GetNextCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 1);
    end;

    // ненужной не нашлось - просто скинем самую мелкую из тех, что есть
    if (result = -1) then
    begin
      result := IndexOfCard(ch2, Party[FCurrPlayer].Cards);
      if (result = -1) then result := GetNextCardIndex(Party[FCurrPlayer].Cards, ch2, 1);
    end;
  end;

  if AINeedPass(FCurrPlayer) then
  begin
    // если своё взял или мизер, скинем самую большую этой масти из тех, что можно скинуть без риска взять
    result := GetMaxCardIndex(tl, Party[FCurrPlayer].Cards);
    while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaPass)) do
      result := GetPrevCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);

    // подходящей нет - скинуть джокера
    if (result = -1) then
    begin
      result := IndexOfCard(cJoker1, Party[FCurrPlayer].Cards);
      if (result = -1) then result := IndexOfCard(cJoker2, Party[FCurrPlayer].Cards);

      if result > -1 then
      begin
        JokerAction := jaCard;
        if Deck = dsz36 then JokerCard := ChangeCardLear(ch6, tl)
        else JokerCard := ChangeCardLear(ch2, tl);
        if (not AIAnalyseCard(JokerCard, aiaPass)) then result := -1;
      end;
    end;

    // безопасно скинуть нечего - придется бить... Кинем самую мелкую этой масти, если ход второй или самую крупную, если последний
    // (на втором ходе известно совершенно однозначно - бьешь ты или нет)
    if result = -1 then
    begin
      if FCurrStep = 2 then GetMaxCardIndex(tl, Party[FCurrPlayer].Cards)
      else result := GetMinCardIndex(tl, Party[FCurrPlayer].Cards);
    end;

    // нет ни выбранной масти ни джокера - придется поискать безопасный козырь (логика как с мастью)
    if (result = -1) then
    begin
      result := GetMaxCardIndex(FTrump, Party[FCurrPlayer].Cards);
      while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaPass)) do
        result := GetPrevCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);

      // безопасного козыря нет, просто кидаем самый мелкий, если ход второй или самуй крупный, если последний
      // (на втором ходе известно совершенно однозначно - бьешь ты или нет)
      if result = -1 then
      begin
        if FCurrStep = 2 then GetMaxCardIndex(FTrump, Party[FCurrPlayer].Cards)
        else result := GetMinCardIndex(FTrump, Party[FCurrPlayer].Cards);
      end;
    end;

    // если нет ни этой масти ни козыря ни джокера, просто скинем самую крупную из тех, что есть
    if (result = -1) then
    begin
      result := IndexOfCard(csAce, Party[FCurrPlayer].Cards);
      if (result = -1) then result := GetPrevCardIndex(Party[FCurrPlayer].Cards, csAce, 1);
    end;
  end;

  // если по каким-то причинам не удалось определить карту, то выбираем случайно
  if Rand then result := -1;
  if (result < 0) or (result >= Length(Party[FCurrPlayer].Cards)) then
    result := Random(Length(Party[FCurrPlayer].Cards));

  // определим действия для джокера
  if Party[FCurrPlayer].Cards[result] in [cJoker1, cJoker2] then
  begin
    if AINeedTake(FCurrPlayer) then
    begin
      JokerAction := jaCard;
      if StrongJoker or (FTrump = lnNone) then JokerCard := ChangeCardLear(chAce, tl)
      else JokerCard := ChangeCardLear(chAce, FTrump);
      //if (not AIAnalyseCard(JokerCard, aiTake)) then result := -1;
    end;

    if AINeedPass(FCurrPlayer) then
    begin
      JokerAction := jaCard;
      if Deck = dsz36 then JokerCard := ChangeCardLear(ch6, tl)
      else JokerCard := ChangeCardLear(ch2, tl);
      //if (not AIAnalyseCard(JokerCard, aiPass)) then result := -1;
    end;

    // если карту для джокера не оперделили - выбираем наугад
    {if result = -1 then result := IndexOfCard(cJoker1, Party[FCurrPlayer].Cards);
    if result = -1 then result := IndexOfCard(cJoker2, Party[FCurrPlayer].Cards);
    JokerAction := jaCard;
    if Random(2) = 0 then
    begin
      if Deck = dsz36 then JokerCard := ChangeCardLear(ch6, tl)
      else JokerCard := ChangeCardLear(ch2, tl);
    end else
      JokerCard := ChangeCardLear(chAce, tl);}
  end;
end;

function TCustomGame.AICalcOrder: integer;

  function _getDark: integer;
  begin
    repeat
      result := Random(Round(FDeals[FCurrDealNo].CardCount / 2));
    until result > 1;
  end;

  function _getBrow: integer;
  var
    i, n: integer;
    maxCard, currCard: TCard;
    takeIdx: integer;

  begin
    case Player[FCurrPlayer].Difficulty of
      //dfEasy: result := Random(FDeals[FCurrDealNo].CardCount + 1);
      dfEasy:
      begin
        // если у любого из игроков есть любой козырь или джокер, то пасуем, иначе:
        // если твой ход первый, то заказываем, иначе, если у игроков есть ТКД любой масти, то пасуем
        result := FDeals[FCurrDealNo].CardCount;
        for i := 0 to Length(Party) - 1 do
        begin
          if i = FCurrPlayer then continue;
          if (Party[i].Cards[0] in [cJoker1, cJoker2]) or (GetCardLear(Party[i].Cards[0]) = FTrump) then
          begin
            result := 0;
            exit;
          end;
          if (FCurrStep <> 0) and (ChangeCardLear(Party[i].Cards[0], lnHearts) in [chAce, chKing, chQueen]) then
          begin
            result := 0;
            exit;
          end;
        end;
      end;
      dfNormal, dfHard:
      begin
        // определим, кто бьет - если этот игрок, то заказать, если нет, то пас (учитывая, кто первый ходит)
        result := FDeals[FCurrDealNo].CardCount;

        i := -1;
        for n := 0 to 2 do
        begin
          if (i < 0) then
            i := FDeals[FCurrDealNo].Player
          else begin
            if i = 2 then i := 0
            else Inc(i);
          end;

          if n = 0 then
          begin
            takeIdx := i;
            maxCard := Party[i].Cards[0];
            if maxCard in [cJoker1, cJoker2] then break;
            continue;
          end;

          currCard := Party[i].Cards[0];
          if currCard in [cJoker1, cJoker2] then
          begin
            takeIdx := i;
            break;
          end;

          if GetCardLear(currCard) = GetCardLear(maxCard) then
          begin
            maxCard := TCard(Max(Ord(maxCard), Ord(currCard)));
            if maxCard = currCard then takeIdx := i;
          end else
          begin
            if GetCardLear(currCard) = FTrump then
            begin
              maxCard := currCard;
              takeIdx := i;
            end;
          end;
        end;

        if takeIdx <> FCurrPlayer then result := 0;
      end;
    end;
  end;

  function _getNormal: integer;
  var
    i, cnt, n, old: integer;

  begin
    result := 0;

    case Deck of
      dsz36: n := 3;
      dsz54: n := 5;
    end;
    
    for i := 0 to Length(Party[FCurrPlayer].Cards) - 1 do
    begin
      if Length(Party[FCurrPlayer].Cards) <= n then
      begin
        cnt := Length(Party[FCurrPlayer].Cards);
        if (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then
        begin
          Inc(result);
          SetLength(Party[FCurrPlayer].OrderCards, Length(Party[FCurrPlayer].OrderCards) + 1);
          Party[FCurrPlayer].OrderCards[High(Party[FCurrPlayer].OrderCards)] := Party[FCurrPlayer].Cards[i];
          continue;
        end;
      end else
        cnt := CountCards(GetCardLear(Party[FCurrPlayer].Cards[i]), Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[i]);

      case Deck of
        dsz36:
        begin
          if (Length(Party[FCurrPlayer].Cards) > 3) and (Length(Party[FCurrPlayer].Cards) <= 4) then Inc(cnt, 3);
          if (Length(Party[FCurrPlayer].Cards) > 4) and (Length(Party[FCurrPlayer].Cards) <= 7) then Inc(cnt, 2);
          if (Length(Party[FCurrPlayer].Cards) > 8) and (Length(Party[FCurrPlayer].Cards) < 12) then Inc(cnt, 1);
        end;
        dsz54:
        begin
          if (Length(Party[FCurrPlayer].Cards) > 5) and (Length(Party[FCurrPlayer].Cards) <= 7) then Inc(cnt, 3);
          if (Length(Party[FCurrPlayer].Cards) > 8) and (Length(Party[FCurrPlayer].Cards) <= 11) then Inc(cnt, 2);
          if (Length(Party[FCurrPlayer].Cards) > 12) and (Length(Party[FCurrPlayer].Cards) < 17) then Inc(cnt, 1);
        end;
      end;

      old := result;
      if Party[FCurrPlayer].Cards[i] in [cJoker1, cJoker2, chAce, cdAce, ccAce, csAce] then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [chKing, cdKing, ccKing, csKing]) and (cnt > 0) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [chQueen, cdQueen, ccQueen, csQueen]) and (cnt > 1) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [chJack, cdJack, ccJack, csJack]) and (cnt > 2) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch10, cd10, cc10, cs10]) and (cnt > 3) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch9, cd9, cc9, cs9]) and (cnt > 4) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch8, cd8, cc8, cs8]) and (cnt > 5) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch7, cd7, cc7, cs7]) and (cnt > 6) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch6, cd6, cc6, cs6]) and (cnt > 7) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch5, cd5, cc5, cs5]) and (cnt > 8) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch4, cd4, cc4, cs4]) and (cnt > 9) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch3, cd3, cc3, cs3]) and (cnt > 10) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch2, cd2, cc2, cs2]) and (cnt > 11) and
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump) then Inc(result);

      if result > old then
      begin
        SetLength(Party[FCurrPlayer].OrderCards, Length(Party[FCurrPlayer].OrderCards) + 1);
        Party[FCurrPlayer].OrderCards[High(Party[FCurrPlayer].OrderCards)] := Party[FCurrPlayer].Cards[i];
      end;
    end;
  end;

  function _getNoTrump: integer;
  var
    i, cnt, n, old: integer;

  begin
    result := 0;

    case Deck of
      dsz36: n := 3;
      dsz54: n := 5;
    end;

    for i := 0 to Length(Party[FCurrPlayer].Cards) - 1 do
    begin
      if Length(Party[FCurrPlayer].Cards) <= n then
        cnt := Length(Party[FCurrPlayer].Cards)
      else
        cnt := CountCards(GetCardLear(Party[FCurrPlayer].Cards[i]), Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[i]);

      case Deck of
        dsz36:
        begin
          if (Length(Party[FCurrPlayer].Cards) > 3) and (Length(Party[FCurrPlayer].Cards) <= 4) then Inc(cnt, 3);
          if (Length(Party[FCurrPlayer].Cards) > 4) and (Length(Party[FCurrPlayer].Cards) <= 7) then Inc(cnt, 2);
          if (Length(Party[FCurrPlayer].Cards) > 8) and (Length(Party[FCurrPlayer].Cards) < 12) then Inc(cnt, 1);
        end;
        dsz54:
        begin
          if (Length(Party[FCurrPlayer].Cards) > 5) and (Length(Party[FCurrPlayer].Cards) <= 7) then Inc(cnt, 3);
          if (Length(Party[FCurrPlayer].Cards) > 8) and (Length(Party[FCurrPlayer].Cards) <= 11) then Inc(cnt, 2);
          if (Length(Party[FCurrPlayer].Cards) > 12) and (Length(Party[FCurrPlayer].Cards) < 17) then Inc(cnt, 1);
        end;
      end;

      old := result;
      if Party[FCurrPlayer].Cards[i] in [cJoker1, cJoker2, chAce, cdAce, ccAce, csAce] then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [chKing, cdKing, ccKing, csKing]) and (cnt > 0) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [chQueen, cdQueen, ccQueen, csQueen]) and (cnt > 1) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [chJack, cdJack, ccJack, csJack]) and (cnt > 2) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch10, cd10, cc10, cs10]) and (cnt > 3) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch9, cd9, cc9, cs9]) and (cnt > 4) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch8, cd8, cc8, cs8]) and (cnt > 5) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch7, cd7, cc7, cs7]) and (cnt > 6) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch6, cd6, cc6, cs6]) and (cnt > 7) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch5, cd5, cc5, cs5]) and (cnt > 8) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch4, cd4, cc4, cs4]) and (cnt > 9) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch3, cd3, cc3, cs3]) and (cnt > 10) then Inc(result);
      if (Party[FCurrPlayer].Cards[i] in [ch2, cd2, cc2, cs2]) and (cnt > 11) then Inc(result);
      if result > old then
      begin
        SetLength(Party[FCurrPlayer].OrderCards, Length(Party[FCurrPlayer].OrderCards) + 1);
        Party[FCurrPlayer].OrderCards[High(Party[FCurrPlayer].OrderCards)] := Party[FCurrPlayer].Cards[i];
      end;
    end;
  end;

  function _getCoeff: integer;
  var
    i, n: integer;
    //a: array[0..1] of integer;

  begin
    result := -1;

    {a[0] := -1; a[1] := 1;
    result := RandomFrom(a);}

    case Deck of
      dsz36: n := 8;
      dsz54: n := 11;
    end;

    for i := 0 to Length(Party[FCurrPlayer].Cards) - 1 do
    begin
      if ((Party[FCurrPlayer].Cards[i] in [chKing, cdKing, ccKing, csKing, chQueen, cdQueen, ccQueen, csQueen]) {or
        (GetCardLear(Party[FCurrPlayer].Cards[i]) = FTrump)}) and (FDeals[FCurrDealNo].CardCount < n) and
        (not FindCard(Party[FCurrPlayer].Cards[i], Party[FCurrPlayer].OrderCards)) then
      begin
        result := 1;
        break;
      end;
    end;
  end;

var
  i, x: integer;

begin
  // ИИ. рассчет заказа
  result := 0;
  if Party[FCurrPlayer].Order < 0 then Party[FCurrPlayer].Order := 0;

  case FDeals[FCurrDealNo].Deal of
    dGold, dMizer: result := 0;
    dDark: result := _getDark;
    dBrow: result := _getBrow;
    dNormal:
      if FTrump = lnNone then result := _getNoTrump
      else result := _getNormal;
    dNoTrump: result := _getNoTrump;
  end;

  // проверка, что такой заказ делать можно
  if (not (FDeals[FCurrDealNo].Deal in [dGold, dMizer])) and (FCurrStep = 2) then
  begin
    x := result;
    for i := 0 to Length(Party) - 1 do if i <> FCurrPlayer then x := x + Party[i].Order;

    if FDeals[FCurrDealNo].CardCount = x then
    begin
      if result = FDeals[FCurrDealNo].CardCount then i := -1
      else begin
        if result = 0 then i := 1
        else i := _getCoeff;
      end;
      Inc(result, i);
    end;
  end;
end;

procedure TCustomGame.CalcStatistic(CanSkip: boolean);
var
  i, x1, x2: integer;
  s, log: string;
  l: TMsgLabel;

begin
  // рассчет очков за раздачу
  x1 := 10;
  x2 := -10;
  case FDeals[FCurrDealNo].Deal of
    dNormal, dNoTrump, dGold, dMizer: ;
    dDark:
    begin
      x1 := x1 * MultDark;
      x2 := x2 * MultDark;
    end;
    dBrow:
    begin
      x1 := x1 * MultBrow;
      x2 := x2 * MultBrow;
    end;
  end;

  for i := 0 to Length(Party) - 1 do
  begin
    if CanSkip then
    begin
      Party[i].Take := 0;
      Party[i].Scores := 0;
    end else
      case FDeals[FCurrDealNo].Deal of
        dNormal, dNoTrump, dDark, dBrow:
        begin
          if Party[i].Take = Party[i].Order then
          begin
            // взял своё
            if Party[i].Order = 0 then Party[i].Scores := PassPoints
            else Party[i].Scores := Party[i].Take * x1;
          end else if Party[i].Take > Party[i].Order then
          begin
            // перебрал
            Party[i].Scores := Party[i].Take;
          end else if Party[i].Take < Party[i].Order then
          begin
            // недобрал
            if PenaltyMode = 0 then
              Party[i].Scores := (Party[i].Order - Party[i].Take) * x2
            else
              Party[i].Scores := Party[i].Order * x2;
          end;
        end;
        dGold: Party[i].Scores := Party[i].Take * x1;
        dMizer: Party[i].Scores := Party[i].Take * x2;
      end;

    Inc(Party[i].Total, Party[i].Scores);
    s := 'Взял: ' + IntToStr(Party[i].Take) + ', Очки: ' + IntToStr(Party[i].Scores);

    if KeepLog then log := log + Player[i].Name +  ' - заказ: ' + IntToStr(Party[i].Order) + ', взял: ' + IntToStr(Party[i].Take) +
      ', Очки: ' + IntToStr(Party[i].Scores) + ' (' + IntToStr(Party[i].Total) + ')';

    case i of
      0: l := lP1Take;
      1: l := lP2Take;
      2: l := lP3Take;
    end;
    if Assigned(FSetMsgProc) then FSetMsgProc(l, s, 0, false, false);
    if KeepLog then log := log + #13#10;
  end;
  if KeepLog then AddToLog(DataDir + LOG_FILE, 'Конец раздачи'#13#10 + log, Now - GameTime);

  CopyStat(GetCurrId, true);
end;

function TCustomGame.AICalcWalk(var JokerAction: TJokerAction; var JokerCard: TCard): integer;
var
  l, jl: TLearName;
  a: array of integer;
  i, n: integer;

begin
  // ИИ. рассчет хода
  if Party[FCurrPlayer].Take < 0 then Party[FCurrPlayer].Take := 0;
  result := -1;
  if Length(Party[FCurrPlayer].Cards) <= 0 then exit;

  if AINeedTake(FCurrPlayer) then
  begin
    // если еще не взял свое или перебрал или золотая, то надо ходить с 100% бьющих:
    // сначала козырями по убыванию, потом простыми, в порядке убывания старшинства (тузы, короли, дамы ... и т.д.),
    // так перебираем все карты, пока не найдем годную для захода
    {if Player[FCurrPlayer].Difficulty = dfEasy then
    begin
      // для легкой игры порядок нужно несколько изменить: просто ищем в порядке убывания старшинства, все масти вместе
      // не разделяя на козыря и простые
      result := IndexOfCard(csAce, Party[FCurrPlayer].Cards);
      if result = -1 then
        result := GetPrevCardIndex(Party[FCurrPlayer].Cards, csAce, 1);
      while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaTake)) do
        result := GetPrevCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 1);
    end else
    begin}
      if FTrump <> lnNone then
      begin
        result := GetMaxCardIndex(FTrump, Party[FCurrPlayer].Cards);
        while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaTake)) do
          result := GetPrevCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);
      end;

      // подходящего козыря не нашлось, ищем не козырную
      if result = -1 then
      begin
        result := IndexOfCard(csAce, Party[FCurrPlayer].Cards);
        if result = -1 then
          result := GetPrevCardIndex(Party[FCurrPlayer].Cards, csAce, 1);
        while (result > -1) and ((GetCardLear(Party[FCurrPlayer].Cards[result]) = FTrump) or
          (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaTake))) do
          result := GetPrevCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 1);
      end;
    //end;

    // тогда походим джокером (логика определения джокера в конце)
    if result = -1 then result := IndexOfCard(cJoker1, Party[FCurrPlayer].Cards);
    if result = -1 then result := IndexOfCard(cJoker2, Party[FCurrPlayer].Cards);

    // если ничего путного для захода не нашлось, то нужно скинуть так, чтобы выманить крупную нужной масти
    // перебираем карты подряд, сначала козыря по возрастанию, потом простые в порядке возрастания старшинства (шестерки, семерки ... )
    if result = -1 then
    begin
      if FTrump <> lnNone then
      begin
        result := GetMinCardIndex(FTrump, Party[FCurrPlayer].Cards);
        while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaLure)) do
          result := GetNextCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);
      end;

      // подходящего козыря не нашлось, ищем не козырную
      if result = -1 then
      begin
        result := IndexOfCard(ch2, Party[FCurrPlayer].Cards);
        if result = -1 then
          result := GetNextCardIndex(Party[FCurrPlayer].Cards, ch2, 1);
        while (result > -1) and ((GetCardLear(Party[FCurrPlayer].Cards[result]) = FTrump) or
          (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaLure))) do
          result := GetNextCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 1);
      end;
    end;

    // ищем любую ненужную карту, которую можно сбросить - в порядке возрастания, вместе с козырями
    if result = -1 then
    begin
      // ищем ненужную карту
      result := IndexOfCard(ch2, Party[FCurrPlayer].Cards);
      if result = -1 then
        result := GetNextCardIndex(Party[FCurrPlayer].Cards, ch2, 1);
      while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaWaste)) do
        result := GetNextCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 1);
    end;
  end;

  if AINeedPass(FCurrPlayer) then
  begin
    {if Player[FCurrPlayer].Difficulty = dfHard then
    begin
      // если своё взял или мизер, надо ходить самой крупной, что можно кинуть без риска взять
      // сначала козырями по убыванию, потом простыми, в порядке убывания старшинства,
      // так перебираем все карты, пока не найдем годную для захода
      if FTrump <> lnNone then
      begin
        result := GetMaxCardIndex(FTrump, Party[FCurrPlayer].Cards);
        while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaPass)) do
          result := GetPrevCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);
      end;

      // подходящего козыря не нашлось, ищем не козырную
      if result = -1 then
      begin
        result := IndexOfCard(csAce, Party[FCurrPlayer].Cards);
        if result = -1 then
          result := GetPrevCardIndex(Party[FCurrPlayer].Cards, csAce, 1);
        while (result > -1) and ((GetCardLear(Party[FCurrPlayer].Cards[result]) = FTrump) or
          (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaPass))) do
          result := GetPrevCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 1);
      end;
    end else
    begin }
      // если своё взял или мизер, надо ходить самой мелкой, без риска взять

      if FDeals[FCurrDealNo].Deal = dMizer then
      begin
        // на мизерах начинаем всегда с самых мелких и перебираем все вместе, не разделяя по мастям
          result := IndexOfCard(ch2, Party[FCurrPlayer].Cards);
          if result = -1 then
            result := GetNextCardIndex(Party[FCurrPlayer].Cards, ch2, 1);
          while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaPass)) do
            result := GetNextCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 1);
      end else
      begin
        // сначала козырями по возрастанию, потом простыми, в порядке возрастания старшинства,
        // так перебираем все карты, пока не найдем годную для захода
        if FTrump <> lnNone then
        begin
          result := GetMinCardIndex(FTrump, Party[FCurrPlayer].Cards);
          while (result > -1) and (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaPass)) do
            result := GetNextCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 0);
        end;

        // подходящего козыря не нашлось, ищем не козырную
        if result = -1 then
        begin
          result := IndexOfCard(ch2, Party[FCurrPlayer].Cards);
          if result = -1 then
            result := GetNextCardIndex(Party[FCurrPlayer].Cards, ch2, 1);
          while (result > -1) and ((GetCardLear(Party[FCurrPlayer].Cards[result]) = FTrump) or
            (not AIAnalyseCard(Party[FCurrPlayer].Cards[result], aiaPass))) do
            result := GetNextCardIndex(Party[FCurrPlayer].Cards, Party[FCurrPlayer].Cards[result], 1);
        end;
      end;
    //end;

    // тогда походим джокером (логика определения джокера в конце)
    if result = -1 then result := IndexOfCard(cJoker1, Party[FCurrPlayer].Cards);
    if result = -1 then result := IndexOfCard(cJoker2, Party[FCurrPlayer].Cards);

    // ходим самой мелкой из того, что есть
    if result = -1 then
    begin
     { SetLength(a, 0);
      for i := 0 to 3 do
        if CountCards(TLearName(i), Party[FCurrPlayer].Cards) > 0 then
        begin
          SetLength(a, Length(a) + 1);
          a[High(a)] := i;
        end;

      if Length(a) = 0 then l := TLearName(RandomRange(Ord(lnHearts), Ord(lnNone)))
      else l := TLearName(RandomFrom(a));

      result := GetMinCardIndex(l, Party[FCurrPlayer].Cards); }
      
      result := IndexOfCard(ch2, Party[FCurrPlayer].Cards);
      if result = -1 then
        result := GetNextCardIndex(Party[FCurrPlayer].Cards, ch2, 1);
    end;
  end;

  // если по каким-то причинам не удалось определить карту, то выбираем случайно
  if (result < 0) or (result >= Length(Party[FCurrPlayer].Cards)) then
    result := Random(Length(Party[FCurrPlayer].Cards));

  // джокеры
  if Party[FCurrPlayer].Cards[result] in [cJoker1, cJoker2] then
  begin
    n := 0;
    if AINeedTake(FCurrPlayer) then
    begin
      // если надо брать - это будет Туз случайной масти из тех, что есть на руках + козырь. И случайное из доступных
      // действий из тех, на которые джокер берет. + проверка, что выбранная карта не будет побита.

      repeat
        Inc(n);
        // определяем доступные действия для джокера
        if (Length(Party[FCurrPlayer].Cards) > 1) then
        begin
          SetLength(a, 1);
          a[0] := Ord(jaCard);

          if JokerMajorLear and ((Party[FCurrPlayer].Order - Party[FCurrPlayer].Take) <> 1) then
          begin
            SetLength(a, Length(a) + 1);
            a[High(a)] := Ord(jaByMax);
          end else if JokerMinorLear and ((Party[FCurrPlayer].Order - Party[FCurrPlayer].Take) = 1) then
          begin
            SetLength(a, Length(a) + 1);
            a[High(a)] := Ord(jaByMin);
          end;
          JokerAction := TJokerAction(RandomFrom(a));
        end else
          JokerAction := jaCard;

        // определяем случайно масть из тех, что на руках + козырь
        SetLength(a, 0);
        if FTrump <> lnNone then
        begin
          SetLength(a, 1);
          a[High(a)] := Ord(FTrump);
        end;
        for i := 0 to 3 do
          if CountCards(TLearName(i), Party[FCurrPlayer].Cards, cJoker2) > 0 then
          begin
            SetLength(a, Length(a) + 1);
            a[High(a)] := i;
          end;

        if Length(a) = 0 then jl := TLearName(RandomRange(Ord(lnHearts), Ord(lnNone)))
        else jl := TLearName(RandomFrom(a));

        JokerCard := ChangeCardLear(chAce, jl);
      until AIAnalyseCard(JokerCard, aiaTake) or (n > CYCLE_STEP_LIMIT);
    end;

    if AINeedPass(FCurrPlayer) then
    begin
      // надо скинуть - выдаем джокера за самую мелкую карту случайной масти + проверка, что ты на эту карту ненароком не возьмешь
      repeat
        Inc(n);
        JokerAction := jaCard;

        SetLength(a, 0);
        for i := 0 to 3 do
          if (TLearName(i) <> FTrump) {and (CountCards(TLearName(i), Party[FCurrPlayer].Cards, cJoker2) > 0)} then
          begin
            SetLength(a, Length(a) + 1);
            a[High(a)] := i;
          end;

        if Length(a) = 0 then jl := TLearName(RandomRange(Ord(lnHearts), Ord(lnNone)))
        else jl := TLearName(RandomFrom(a));

        if Deck = dsz36 then JokerCard := ChangeCardLear(ch6, jl)
        else JokerCard := ChangeCardLear(ch2, jl);
      until AIAnalyseCard(JokerCard, aiaPass) or (n > CYCLE_STEP_LIMIT);
    end;
  end;
end;

function TCustomGame.AICanPass(pIdx: integer; Card: TCard): boolean;
var
  l: TLearName;
  i: integer;

begin
  // определяет, что данный игрок может скинуть на эту карту в данный момент
  result := false;
  l := GetCardLear(Card);

  case Player[FCurrPlayer].Difficulty of
    dfEasy: // анализ по вышедшему
    begin
      // если масть у игрока вышла
      if FindReleasedLear(l, pIdx) then
      begin
        // если возможно бить козырем и козыря нет - точно скинет
        if (FTrump <> lnNone) and (l <> FTrump) and FindReleasedLear(FTrump, pIdx) then result := true;
        exit;
      end;

      // если масть есть - посмотрим вышедшие карты. Если не вышло что-то из того, что меньше, то вероятность, что скинет есть
      for i := StartLearCardOrd(l) to Ord(Card) - 1 do
        if not FindReleasedCard(TCard(i)) then
        begin
          result := true;
          exit;
        end;
    end;
    dfNormal, dfHard: // анализ по картам игрока
    begin
      // масть вышла
      if not FindCardLear(l, Party[pIdx].Cards) then
      begin
        // если возможно бить козырем и козыря нет - точно скинет
        if (FTrump <> lnNone) and (l <> FTrump) and (not FindCardLear(FTrump, Party[pIdx].Cards)) then result := true;
        exit;
      end;

      // если масть есть - посмотрим карты. Если есть что-то из того, что меньше, то вероятность, что скинет есть
      for i := StartLearCardOrd(l) to Ord(Card) - 1 do
        if FindCard(TCard(i), Party[pIdx].Cards) then
        begin
          result := true;
          exit;
        end;
    end;
  end;
end;

function TCustomGame.AICanTake(pIdx: integer; Card: TCard): boolean;
var
  l: TLearName;
  i: integer;

begin
  // определяет, что данный игрок может побить эту карту в данный момент
  result := false;
  l := GetCardLear(Card);

  case Player[FCurrPlayer].Difficulty of
    dfEasy: // анализ по вышедшему
    begin
      // если масть у игрока вышла
      if FindReleasedLear(l, pIdx) then
      begin
        // если возможно бить козырем и козыри есть - точно побьет
        if (FTrump <> lnNone) and (l <> FTrump) and (not FindReleasedLear(FTrump, pIdx)) then result := true;
        exit;
      end;

      // если масть есть - посмотрим вышедшие карты. Если не вышло что-то из того, что больше, то вероятность, что сможет побить есть
      for i := Ord(Card) + 1 to EndLearCardOrd(l) do
        if not FindReleasedCard(TCard(i)) then
        begin
          result := true;
          exit;
        end;
    end;
    dfNormal, dfHard: // анализ по картам игрока
    begin
      // масть вышла
      if not FindCardLear(l, Party[pIdx].Cards) then
      begin
        // если возможно бить козырем и козыри есть - точно побьет
        if (FTrump <> lnNone) and (l <> FTrump) and FindCardLear(FTrump, Party[pIdx].Cards) then result := true;
        exit;
      end;

      // если масть есть - посмотрим карты. Если есть что-то из того, что больше, то вероятность, что сможет побить есть
      for i := Ord(Card) + 1 to EndLearCardOrd(l) do
        if FindCard(TCard(i), Party[pIdx].Cards) then
        begin
          result := true;
          exit;
        end;
    end;
  end;
end;

function TCustomGame.CardToStr(c: TCard; AddLear: boolean; Short: boolean): string;
begin
  result := '';
  if AddLear then result := iif(Short, '', ' ') + LearToStr(GetCardLear(c), '', Short);
  case c of
    ch2, cd2, cc2, cs2: result := '2' + result;
    ch3, cd3, cc3, cs3: result := '3' + result;
    ch4, cd4, cc4, cs4: result := '4' + result;
    ch5, cd5, cc5, cs5: result := '5' + result;
    ch6, cd6, cc6, cs6: result := '6' + result;
    ch7, cd7, cc7, cs7: result := '7' + result;
    ch8, cd8, cc8, cs8: result := '8' + result;
    ch9, cd9, cc9, cs9: result := '9' + result;
    ch10, cd10, cc10, cs10: result := '10' + result;
    chJack, cdJack, ccJack, csJack: result := iif(Short, 'В', 'Валет') + result;
    chQueen, cdQueen, ccQueen, csQueen: result := iif(Short, 'Д', 'Дама') + result;
    chKing, cdKing, ccKing, csKing: result := iif(Short, 'К', 'Король') + result;
    chAce, cdAce, ccAce, csAce: result := iif(Short, 'Т', 'Туз') + result;
    cJoker1, cJoker2: result := iif(Short, 'Дж', 'Джокер');
  end;
end;

procedure TCustomGame.ClearParty;
var
  i: integer;

begin
  for i := 0 to Length(Party) - 1 do
  begin
    Party[i].Index := -1;
    Party[i].Order := -1;
    Party[i].Take := -1;
    Party[i].Scores := 0;
    Party[i].Total := 0;
    SetLength(Party[i].Cards, 0);
    SetLength(Party[i].OrderCards, 0);
  end;
end;

constructor TCustomGame.Create(AStatTbl: TMemTableEh; ADrawProc: TDrawProc; ASetProc: TSetProc; ASetMsgProc: TSetMessageProc);
var
  i: integer;
  
begin
  inherited Create;
  for i := 0 to Length(FLearOrder) - 1 do FLearOrder[i] := TLearName(i);
  SetLength(Players, 0);
  StatTable := AStatTbl;
  FDrawProc := ADrawProc;
  FSetPlayerConProc := ASetProc;
  FSetMsgProc := ASetMsgProc;
  InitializeGameData(true);
end;

procedure TCustomGame.DealCards;
var
  pi, i: integer;
  randRange: array of integer;
  Waste: TCards;
  f: boolean;
  c: TCard;
  cs: TCardSet;
  log: string;
  
begin
  // поднимаем номер текущей раздачи
  Inc(FCurrDealNo);
  CanNextDeal := false;
  CanPause := true;

  // если № раздачи вышел за рамки массива раздач - это конец игры
  if FCurrDealNo >= Length(FDeals) then
  begin
    EndGame;
    exit;
  end;

  // устанавливаем первого игрока
  noPause := false;
  TakePlayer := -1;
  FCurrPlayer := FDeals[FCurrDealNo].Player;
  case FDeals[FCurrDealNo].Deal of
    dGold, dMizer:
    begin
      FBet := false;
      noPause := true;
    end else FBet := true;
  end;

  f := FDeals[FCurrDealNo].Deal <> prevDeal;
  prevDeal := FDeals[FCurrDealNo].Deal;
  if Assigned(FSetMsgProc) then FSetMsgProc(lDeal, 'Раздача: ' + DealToStr(FDeals[FCurrDealNo], true) +
    '. Первый ход: ' + Player[FCurrPlayer].Name, 0, true, f);
  if Assigned(FSetMsgProc) then FSetMsgProc(lInfo, 'Раздаю карты', WaitDelay, false, false);

  SetLength(randRange, DeckSz);
  case Deck of
    dsz36:
    begin
      i := 0;
      if NoJoker then cs := [ch6..chAce, cd6..cdAce, cc6..ccAce, cs6..csAce]
      else cs := [ch6..chAce, cd6..cdAce, cc6..ccAce, cs6, cs8..csAce, cJoker2];
      for c in cs do
      begin
        randRange[i] := Ord(c);
        Inc(i);
      end;
    end;
    dsz54:
    begin
      i := 0;
      if NoJoker then cs := [ch2..ccAce, cs3..csAce]
      else cs := [ch2..cJoker2];
      for c in cs do
      begin
        randRange[i] := Ord(c);
        Inc(i);
      end;
    end;
  end;

  // определяем козырную масть
  if FDeals[FCurrDealNo].Deal = dNoTrump then FTrump := lnNone
  else FTrump := GenerateTrump(0, 54);
  // собственно раздаем карты, начиная с текущего и по кругу каждому
  SetLength(Waste, 0);
  //Randomize;
  for pi := 0 to Length(Party) - 1 do
  begin
    SetLength(Party[pi].Cards, FDeals[FCurrDealNo].CardCount);
    for i := 1 to FDeals[FCurrDealNo].CardCount do
    begin
      // тут получаем следующую карту случайным образом
      f := true;
      while f or FindCard(Party[pi].Cards[i-1], Waste) do
      begin
        f := false;
        Party[pi].Cards[i-1] := TCard(RandomFrom(randRange));
      end;
      SetLength(Waste, Length(Waste) + 1);
      Waste[High(Waste)] := Party[pi].Cards[i-1];
    end;
  end;

  if FSortDirect in [sdAsc, sdDesc] then
    for pi := 0 to Length(Party) - 1 do SortPlayerCards(pi);

  // лог
  if KeepLog then
  begin
    log := 'Раздача: ' + DealToStr(FDeals[FCurrDealNo], true) + '. Козырь: ' + LearToStr(FTrump, 'нет') +
      '. Первый ход: ' + Player[FCurrPlayer].Name;

    for pi := 0 to Length(Party) - 1 do
    begin
      log := log + #13#10 + Player[pi].Name + ':';
      for i := 0 to Length(Party[pi].Cards) - 1 do
        log := log + ' ' + CardToStr(Party[pi].Cards[i], true, true);
    end;

    AddToLog(DataDir + LOG_FILE, log, Now - GameTime);
  end;

  // встать на строку таблицы
  StatTable.Locate('ID', GetCurrId, []);
  if Assigned(FDrawProc) then FDrawProc(false);
  Sleep(WaitDelay);
end;

function TCustomGame.DealToStr(d: TDeal; Full: boolean): string;
begin
  case d.Deal of
    dNormal: result := iif(Full, 'по ' + IntToStr(d.CardCount), IntToStr(d.CardCount));
    dNoTrump: result := iif(Full, 'Бескозырка', 'Б');
    dDark: result := iif(Full, 'Темная', 'Т');
    dGold: result := iif(Full, 'Золотая', 'З');
    dMizer: result := iif(Full, 'Мизер', 'М');
    dBrow: result := iif(Full, 'Лобовая', 'Л');
  end;
end;

procedure TCustomGame.DelCard(pIdx, CardIndex: integer);
var
  i: integer;

begin
  if (pIdx < 0) or (pIdx >= Length(Party)) then exit;
  if (CardIndex < 0) or (CardIndex >= Length(Party[pIdx].Cards)) then exit;

  if CardIndex < (Length(Party[pIdx].Cards) - 1) then
    for i := CardIndex + 1 to Length(Party[pIdx].Cards) - 1 do
      Party[pIdx].Cards[i-1] := Party[pIdx].Cards[i];

  SetLength(Party[pIdx].Cards, Length(Party[pIdx].Cards) - 1);
end;

procedure TCustomGame.DelOrderCard(pIdx, CardIndex: integer);
var
  i: integer;

begin
  if (pIdx < 0) or (pIdx >= Length(Party)) then exit;
  if (CardIndex < 0) or (CardIndex >= Length(Party[pIdx].OrderCards)) then exit;

  if CardIndex < (Length(Party[pIdx].OrderCards) - 1) then
    for i := CardIndex + 1 to Length(Party[pIdx].OrderCards) - 1 do
      Party[pIdx].OrderCards[i-1] := Party[pIdx].OrderCards[i];

  SetLength(Party[pIdx].OrderCards, Length(Party[pIdx].OrderCards) - 1);
end;

destructor TCustomGame.Destroy;
begin
  SetLength(Players, 0);
  InitializeGameData(true);
  inherited Destroy;
end;

procedure TCustomGame.FillDeals;

  procedure AddDeal(cCount, cMax: integer; d: TSpecDeal);
  var
    i, n: integer;

  begin
    if LongGame or (cCount = cMax) then n := Length(Party) - 1
    else n := 0;

    for i := 0 to n do
    begin
      SetLength(FDeals, Length(FDeals) + 1);
      FDeals[High(FDeals)].Player := i;
      FDeals[High(FDeals)].CardCount := cCount;
      FDeals[High(FDeals)].Deal := d;
    end;
  end;

var
  cMin, cMax, step, cCurr, i: integer;

begin
  if FStarted then exit;

  // без нечетных
  if not (goNotEven in GameOptions) then cMin := 2
  else cMin := 1;
  // шаг
  if (not (goNotEven in GameOptions)) or (not (goEven in GameOptions)) then step := 2
  else step := 1;
  // макс. кол-во карт в раздаче
  cMax := DeckSz div 3;

  // обычные раздачи
  // возрастающие
  if goAsc in GameOptions then
  begin
    cCurr := cMin;
    while cCurr <= cMax do
    begin
      AddDeal(cCurr, cMax, dNormal);
      Inc(cCurr, step);
    end;
  end;

  // убывающие
  if goDesc in GameOptions then
  begin
    cCurr := cMax - step;
    while cCurr >= cMin do
    begin
      AddDeal(cCurr, cMax, dNormal);
      Inc(cCurr, -step);
    end;
  end;

  // специальные раздачи
  if goNoTrump in GameOptions then AddDeal(cMax, cMax, dNoTrump);
  if goDark in GameOptions then AddDeal(cMax, cMax, dDark);
  if goGold in GameOptions then AddDeal(cMax, cMax, dGold);
  if goMizer in GameOptions then AddDeal(cMax, cMax, dMizer);
  if goBrow in GameOptions then AddDeal(1, 1, dBrow);

  // в короткой надо раскидать раздачи по игрокам
  if not LongGame then
  begin
    cCurr := 0;
    for i := 0 to Length(FDeals) - 1 do
    begin
      FDeals[i].Player := cCurr;
      cCurr := GetNextIndex(cCurr);
    end;
  end;

  // теперь надо залить таблицу
  FillStatTable;
  prevDeal := FDeals[0].Deal;
end;

procedure TCustomGame.FillStatTable;
var
  i: integer;

begin
  StatTable.DisableControls;
  try
    for i := 0 to Length(FDeals) - 1 do
    begin
      StatTable.Append;
      StatTable.FieldByName('DEAL_NO').AsInteger := i + 1;
      StatTable.FieldByName('ID').AsInteger := i + 1;
      StatTable.FieldByName('DEAL_NAME').AsString := DealToStr(FDeals[i]);
      StatTable.Post;
    end;
  finally
    StatTable.EnableControls;
  end;
end;

function TCustomGame.FindCard(Card: TCard; Cards: TCards; Offset: integer): boolean;
var
  i: integer;

begin
  // Есть ли карта Card
  result := true;
  for i := Offset to Length(Cards) - 1 do
    if Cards[i] = Card then exit;

  result := false;
end;

function TCustomGame.FindCard(Card: TCard; Lear: TLearName; Cards: TCards; Offset: integer): boolean;
var
  i: integer;

begin
  // Есть ли карта такого же достоинства, как Card, но указанной масти
  result := true;
  for i := Offset to Length(Cards) - 1 do
    if Cards[i] = ChangeCardLear(Card, Lear) then exit;

  result := false;
end;

function TCustomGame.FindCardLear(Lear: TLearName; Cards: TCards; ExCard: TCard): boolean;
var
  i: integer;

begin
  // есть ли карта указанной масти, исключая ExCard
  result := true;
  for i := 0 to Length(Cards) - 1 do
    if (GetCardLear(Cards[i]) = Lear) and (Cards[i] <> ExCard) then exit;

  result := false;
end;

function TCustomGame.FindReleasedCard(Card: TCard; pIdx: integer): boolean;
begin
  result := IndexOfReleasedCard(Card, pIdx) > -1;
end;

function TCustomGame.FindReleasedCard(Card: TCard): boolean;
begin
  result := IndexOfReleasedCard(Card) > -1;
end;

function TCustomGame.FindReleasedLear(Lear: TLearName; pIdx: integer): boolean;
begin
  result := IndexOfReleasedLear(Lear, pIdx) > -1;
end;

function TCustomGame.IndexOfReleasedCard(Card: TCard; pIdx: integer): integer;
var
  i: integer;

begin
  // находит индекс вышедшей карты в массиве по пользователю
  result := -1;
  for i := 0 to Length(FReleasedCards) - 1 do
    if (FReleasedCards[i].Card = Card) and (FReleasedCards[i].Player = pIdx) then
    begin
      result := i;
      exit;
    end;
end;

function TCustomGame.IndexOfReleasedCard(Card: TCard): integer;
var
  i: integer;

begin
  // находит индекс вышедшей карты в массиве
  result := -1;
  for i := 0 to Length(FReleasedCards) - 1 do
    if (FReleasedCards[i].Card = Card) then
    begin
      result := i;
      exit;
    end;
end;

function TCustomGame.IndexOfReleasedLear(Lear: TLearName; pIdx: integer): integer;
var
  i: integer;

begin
  // находит индекс вышедшей масти в массиве по пользователю
  result := -1;
  for i := 0 to Length(FReleasedLears) - 1 do
    if (FReleasedLears[i].Lear = Lear) and (FReleasedLears[i].Player = pIdx) then
    begin
      result := i;
      exit;
    end;
end;

function TCustomGame.FindCardLear(Lear: TLearName; Cards: TCards): boolean;
var
  i: integer;

begin
  // есть ли карта указанной масти
  result := true;
  for i := 0 to Length(Cards) - 1 do
    if GetCardLear(Cards[i]) = Lear then exit;

  result := false;
end;

function TCustomGame.GenerateTrump(cFrom, cTo: integer): TLearName;
begin
  result := GetCardLear(TCard(RandomRange(cFrom, cTo)));
end;

function TCustomGame.GetCardLear(Card: TCard): TLearName;
begin
  case Card of
    ch2..chAce: result := lnHearts;
    cd2..cdAce: result := lnDiamonds;
    cc2..ccAce: result := lnClubs;
    cs2..csAce: result := lnSpades;
    else result := lnNone;
  end;
end;

function TCustomGame.GetCurrDeal: TDeal;
begin
  result := FDeals[FCurrDealNo];
end;

function TCustomGame.GetCurrId: integer;
begin
  result := FCurrDealNo + 1;
end;

function TCustomGame.GetMaxCard(Lear: TLearName; Cards: TCards): TCard;
begin
  result := Cards[GetMaxCardIndex(Lear, Cards)];
end;

function TCustomGame.GetMaxCardIndex(Lear: TLearName; Cards: TCards): integer;
var
  i: integer;

begin
  result := IndexOfCardLear(Lear, Cards);
  if result = -1 then exit;

  for i := result + 1 to Length(Cards) - 1 do
    if GetCardLear(Cards[i]) = Lear then
      if TCard(Max(Ord(Cards[result]), Ord(Cards[i]))) = Cards[i] then result := i;
end;

function TCustomGame.GetMinCard(Lear: TLearName; Cards: TCards): TCard;
begin
  result := Cards[GetMinCardIndex(Lear, Cards)];
end;

function TCustomGame.GetMinCardIndex(Lear: TLearName; Cards: TCards): integer;
var
  i: integer;

begin
  result := IndexOfCardLear(Lear, Cards);
  if result = -1 then exit;

  for i := result + 1 to Length(Cards) - 1 do
    if GetCardLear(Cards[i]) = Lear then
      if TCard(Min(Ord(Cards[result]), Ord(Cards[i]))) = Cards[i] then result := i;
end;

function TCustomGame.GetNextCard(Cards: TCards; CurrCard: TCard; OrderBy: integer): TCard;
begin
  // находит следующую по величине карту
  // OrderBy: 0 - по масти, 1 - по старшинству без учета масти
  result := Cards[GetNextCardIndex(Cards, CurrCard, OrderBy)];
end;

function TCustomGame.GetNextCardIndex(Cards: TCards; CurrCard: TCard; OrderBy: integer): integer;
var
  i, j, n: integer;

begin
  // находит следующую по величине карту
  // OrderBy: 0 - по масти, 1 - по старшинству без учета масти
  result := -1;

  case OrderBy of
    0:
    begin
      if CurrCard in [chAce, cdAce, ccAce, csAce] then exit;

      for i := Ord(CurrCard) + 1 to EndLearCardOrd(GetCardLear(CurrCard)) do
      begin
        result := IndexOfCard(TCard(i), Cards);
        if result > -1 then exit;
      end;
    end;
    1:
    begin
      if CurrCard = csAce then exit;
      n := Ord(CurrCard) + 13;
      result := IndexOfCard(TCard(n), Cards);
      if result > -1 then exit;

      for i := 1 to Ord(chAce) - Ord(ChangeCardLear(CurrCard, lnHearts)) + 1 do
      begin
        j := 0;
        while true do
        begin
          n := n + j;
          if n > Ord(csAce) then break;
          result := IndexOfCard(TCard(n), Cards);
          if result > -1 then exit;
          j := 13;
        end;
        n := Ord(ChangeCardLear(CurrCard, lnHearts)) + i;
      end;
    end;
  end;
end;

function TCustomGame.GetNextIndex(CurrIndex: integer): integer;
begin
  result := 0;
  if (CurrIndex < 0) or (CurrIndex >= 2) then exit;
  result := CurrIndex + 1;
end;

function TCustomGame.GetPlayer(pIndex: integer): TPlayer;
begin
  // pIndex - индекс игрока в текущей игре, а не в списке всех игроков
  if (pIndex < 0) or (pIndex > 2) then exit;
  result := Players[Party[pIndex].Index];
end;

function TCustomGame.GetPrevCard(Cards: TCards; CurrCard: TCard; OrderBy: integer): TCard;
begin
  // находит предыдущую по величине карту
  // OrderBy: 0 - по масти, 1 - по старшинству без учета масти
  result := Cards[GetPrevCardIndex(Cards, CurrCard, OrderBy)];
end;

function TCustomGame.GetPrevCardIndex(Cards: TCards; CurrCard: TCard; OrderBy: integer): integer;
var
  i, j, n: integer;

begin
  // находит предыдущую по величине карту
  // OrderBy: 0 - по масти, 1 - по старшинству без учета масти
  result := -1;

  case OrderBy of
    0:
    begin
      if CurrCard in [ch2, cd2, cc2, cs2] then exit;

      for i := Ord(CurrCard) - 1 downto StartLearCardOrd(GetCardLear(CurrCard)) do
      begin
        result := IndexOfCard(TCard(i), Cards);
        if result > -1 then exit;
      end;
    end;
    1:
    begin
      if CurrCard = ch2 then exit;
      n := Ord(CurrCard) - 13;
      result := IndexOfCard(TCard(n), Cards);
      if result > -1 then exit;

      for i := 1 to Ord(ChangeCardLear(CurrCard, lnHearts)) - Ord(ch2) + 1 do
      begin
        j := 0;
        while true do
        begin
          n := n - j;
          if n < Ord(ch2) then break;
          result := IndexOfCard(TCard(n), Cards);
          if result > -1 then exit;
          j := 13;
        end;
        n := Ord(ChangeCardLear(CurrCard, lnSpades)) - i;
      end;
    end;
  end;
end;

function TCustomGame.ChangeCardLear(Card: TCard; Lear: TLearName): TCard;
var
  n: integer;

begin
  result := Card;
  if Lear = lnNone then exit;
  if result in [cJoker1, cJoker2] then exit;
  if GetCardLear(result) = Lear then exit;

  case result of
    ch2..chAce:
      case Lear of
        lnHearts: n := 0;
        lnDiamonds: n := 13;
        lnClubs: n := 26;
        lnSpades: n := 39;
      end;
    cd2..cdAce:
      case Lear of
        lnHearts: n := -13;
        lnDiamonds: n := 0;
        lnClubs: n := 13;
        lnSpades: n := 26;
      end;
    cc2..ccAce:
      case Lear of
        lnHearts: n := -26;
        lnDiamonds: n := -13;
        lnClubs: n := 0;
        lnSpades: n := 13;
      end;
    cs2..csAce:
      case Lear of
        lnHearts: n := -39;
        lnDiamonds: n := -26;
        lnClubs: n := -13;
        lnSpades: n := 0;
      end;
  end;

  result := TCard(Ord(result) + n);  
end;

function TCustomGame.ChangeCardLearNoTable(Card: TCard): TCard;
var
  i: integer;
  f: boolean;
  tl: TLearName;

begin
  while true do
  begin
    f := true;
    result := ChangeCardLear(Card, TLearName(RandomRange(Ord(lnHearts), Ord(lnNone))));
    for i := 0 to Length(FTable) - 1 do
    begin
      if FTable[i].Card in [cJoker1, cJoker2] then tl := GetCardLear(FTable[i].JokerCard)
      else tl := GetCardLear(FTable[i].Card);
      if tl = GetCardLear(result) then
      begin
        f := false;
        break;
      end;
    end;
    if f then break;
  end;
end;

function TCustomGame.ChangeCardLearToTable(Card: TCard): TCard;
var
  tl: TLearName;

begin
  result := Card;
  if Length(FTable) = 0 then exit;

  if FTable[0].Card in [cJoker1, cJoker2] then tl := GetCardLear(FTable[0].JokerCard)
  else tl := GetCardLear(FTable[0].Card);

  result := ChangeCardLear(Card, tl);
end;

function TCustomGame.IsLearEnded(Lear: TLearName): boolean;
var
  i: integer;

begin
  result := true;
  for i := StartLearCardOrd(Lear) to EndLearCardOrd(Lear) do
    if not FindReleasedCard(TCard(i)) then
    begin
      result := false;
      exit;
    end;
end;

function TCustomGame.AIIsBeat(Card: TCard): boolean;
var
  i: integer;
  tl, l: TLearName;
  c: TCard;
  
begin
  // проверка - бьет карта или нет (true - бьет, false - нет)
  // если на столе нет карт - то считаем, что бьет
  result := true;
  // если это джокер - то на выход: сюда нужно передавать не джокера, а ту карту, за которую его выдают
  if Card in [cJoker1, cJoker2] then exit;
  if Length(FTable) = 0 then exit;

  if (FTable[0].Card in [cJoker1, cJoker2]) then tl := GetCardLear(FTable[0].JokerCard)
  else tl := GetCardLear(FTable[0].Card);
  l := GetCardLear(Card);

  // если это козырь, то если на столе есть больший козырь - не побил
  if l = FTrump then
  begin
    for i := 0 to Length(FTable) - 1 do
    begin
      if FTable[i].Card in [cJoker1, cJoker2] then c := FTable[i].JokerCard
      else c := FTable[i].Card;
      if ((GetCardLear(c)) = FTrump) and (Card < c) then
      begin
        result := false;
        exit;
      end;
    end;
    exit;
  end;

  // если это масть. Если не та, которой ходили - не побил
  if l <> tl then
  begin
    result := false;
    exit;
  end;

  // если та, то если на столе есть козырь или большая карта этой масти - не побил
  for i := 0 to Length(FTable) - 1 do
  begin
    if FTable[i].Card in [cJoker1, cJoker2] then c := FTable[i].JokerCard
    else c := FTable[i].Card;
    if ((GetCardLear(c)) = FTrump) or ((GetCardLear(c) = tl) and (Card < c)) then
    begin
      result := false;
      exit;
    end;
  end;

  // в остальных случаях побил
end;

function TCustomGame.AINeedPass(pIdx: integer): boolean;
begin
  // определяет, нужно ли на данный момент игроку скидывать
  // true - нужно скидывать
  result := ((FDeals[FCurrDealNo].Deal in [dNormal, dNoTrump, dDark, dBrow]) and (Party[pIdx].Take = Party[pIdx].Order)) or
    (FDeals[FCurrDealNo].Deal = dMizer);
end;

function TCustomGame.AINeedTake(pIdx: integer): boolean;
begin
  // определяет, нужно ли на данный момент игроку брать
  // true - нужно брать
  result := ((FDeals[FCurrDealNo].Deal in [dNormal, dNoTrump, dDark, dBrow]) and (Party[pIdx].Take <> Party[pIdx].Order)) or
    (FDeals[FCurrDealNo].Deal = dGold);
end;

function TCustomGame.JokerActionToStr(JokerAction: TJokerAction; JokerCard: TCard): string;
begin
  result := '';

  case JokerAction of
    jaByMax: result := 'По старшим ' + iif(GetCardLear(JokerCard) = FTrump, 'Козырям', LearToStr(GetCardLear(JokerCard), '') + 'м');
    jaByMin: result := 'По младшим ' + iif(GetCardLear(JokerCard) = FTrump, 'Козырям', LearToStr(GetCardLear(JokerCard), '') + 'м');
    jaCard: result := CardToStr(JokerCard);
  end;
end;

procedure TCustomGame.GiveWalk(CanNextStep: boolean);
var
  f: boolean;
  
begin
  f := FBet;
  if FCurrStep = Length(Party) - 1 then
  begin
    if FBet then FBet := false
    else if Length(Party[High(Party)].Cards) = 0 then CanNextDeal := true;
  end;

  if not f then OldStep := FCurrStep
  else OldStep := -1;
  if TakePlayer = -1 then FCurrPlayer := GetNextIndex(FCurrPlayer)
  else FCurrPlayer := TakePlayer;
  if CanNextStep then FCurrStep := GetNextIndex(FCurrStep);
  if SaveEachStep then SaveGame;
end;

procedure TCustomGame.HoldGame;
begin
  if not FStarted then exit;
  if KeepLog and (not FCanStopGame) then AddToLog(DataDir + LOG_FILE, 'Игра отложена.'#13#10, Now - GameTime);
  SaveGame;
  StopGame(true);
end;

function TCustomGame.AICheckToLure(Card: TCard): boolean;
var
  l: TLearName;
  maxOrder, i: integer;
  oCard, maxCard: TCard;
  cntNeed, cntAv, cnt: integer;
  pl1, pl2: integer;
  
begin
  // смотрим, является ли карта прикрывающей и есть ли на руках то, что она прикрывает
  result := false;
  l := GetCardLear(Card);

  // эта карта что-то прикрывает?
  if FindCard(Card, Party[FCurrPlayer].OrderCards) then exit;
  maxOrder := GetMaxCardIndex(l, Party[FCurrPlayer].OrderCards);
  if maxOrder < 0 then exit;
  oCard := Party[FCurrPlayer].OrderCards[maxOrder];
  maxCard := ChangeCardLear(chAce, l);
  cntNeed := Ord(maxCard) - Ord(oCard);
  cntAv := CountCards(l, Party[FCurrPlayer].Cards, oCard);
  result := cntAv <= cntNeed;
  if not result then exit;

  // вышло ли уже все, что крупнее самой большой прикрываемой карты? если нет - то карта еще прикрывает
  cnt := 0;
  pl1 := GetNextIndex(FCurrPlayer);
  pl2 := GetNextIndex(pl1);

  case Player[FCurrPlayer].Difficulty of
    dfEasy:
    begin
      for i := Ord(oCard) + 1 to EndLearCardOrd(l) do
        if FindReleasedCard(TCard(i)) then Inc(cnt);

      result := cntNeed > cnt;
    end;
    dfNormal, dfHard:
    begin
      for i := Ord(oCard) + 1 to EndLearCardOrd(l) do
        if (not FindCard(TCard(i), Party[pl1].Cards)) and (not FindCard(TCard(i), Party[pl2].Cards)) then Inc(cnt);

      result := cntNeed > cnt;
    end;
  end;
end;

{function TCustomGame.AICheckToPass(Card: TCard): TAiResult;
var
  i, j, pli, plNext: integer;
  l: TLearName;

begin
  result := airUnknown;
  
  // проверка, можно ли, ходя данной картой текущим игроком в текущую очередь, 100% НЕ взять взятку
  if AIIsBeat(Card) then result := airTake
  else result := airPass;

  // на легкой просто анализ ситуации на игровом столе - бьет карта то, что там есть или нет (т.е. когда твой ход первый, результат всегда true)
  if Player[FCurrPlayer].Difficulty = dfEasy then exit;

  // 1. анализ карт на игровом столе (если твой ход первый - анализировать нечего)
  if FCurrStep > 0 then
  begin
    if (result = airTake) or (FCurrStep = 2) then exit;
  end;

  l := GetCardLear(Card);
  plNext := GetNextIndex(FCurrPlayer);
  //pl2 := GetNextIndex(pl1);

  // 2. анализ вышедших мастей
  pli := FCurrPlayer;
  for i := FCurrStep + 1 to 2 do
  begin
    pli := GetNextIndex(pli);

    case Player[FCurrPlayer].Difficulty of
      dfEasy: ; // ничего не сделаешь
      dfNormal:
      begin
        // просматриваем среди вышедших мастей у следующих за текущим игроков
        // если у игрока масть вышла
        if FindReleasedLear(l, pli) then
        begin
          // если у него вышли козыри (если козырь играет) - то он не бьет
          if FTrump <> lnNone then
          begin
            if not FindReleasedLear(FTrump, pli) then
              if (FDeals[FCurrDealNo].Deal in [dNoTrump, dDark, dGold, dMizer]) or ((FDeals[FCurrDealNo].Deal = dNormal) and
                ((FDeals[FCurrDealNo].CardCount = 12) or (FDeals[FCurrDealNo].CardCount = 17))) then
                result := airPass
              else
                result := airUnknown;
          end;
        end else
        begin
          result := airPass;
          
          // если масть осталась - проверим по вышедшим картам
          // пробежимся по всем картам, что меньше проверяемой и поищем среди вышедших
          for j := StartLearCardOrd(l) to Ord(Card) - 1 do
          begin
            // если карта у себя - не смотрим
            if FindCard(TCard(j), Party[FCurrPlayer].Cards) then continue;

            if not FindReleasedCard(TCard(j)) then
            begin
              // карты среди вышедших нет
              // если ход первый, то выходим
              if FCurrStep > 0 then
              begin
                // если ход не первый, то попробуем понять, у кого осталась эта мелкая карта (если у первого, то ок, продолжаем):
                // если у последнего закончилась эта масть, значит карта у первого - продолжаем; иначе карта может быть у любого - выход
                if not FindReleasedLear(l, pl1) then result := airUnknown;
              end else
                result := airUnknown;
            end;
          end;
        end;

        if result <> airPass then exit;
      end;
      dfHard:
      begin
        // просматриваем среди карт у следующих за текущим игроков
        // если у игрока масть вышла
        if not FindCardLear(l, Party[pli].Cards) then
        begin
          // если у него вышли козыри (если козырь играет) - то он не бьет
          if (FTrump = lnNone) or (not FindCardLear(FTrump, Party[pli].Cards)) then result := airTake
          else
          begin
            result := airPass;
            exit;
          end;
        end else
        begin
          result := airPass;

          for j := StartLearCardOrd(l) to Ord(Card) - 1 do
            if FindCard(TCard(j), Party[pli].Cards) then
            begin
              result := airUnknown;
              exit;
            end;
        end;
      end;
    end;
  end;
end;}

function TCustomGame.AICheckToTake(Card: TCard): TAiResult;
var
  i, j, pli, plNext: integer;
  l: TLearName;
  
begin
  // проверка, что можно сделать, ходя данной картой текущим игроком в текущую очередь: 100% взять, 100% слить или неясно
  result := airUnknown;

  if AIIsBeat(Card) then result := airTake
  else result := airPass;

  // на легкой просто анализ ситуации на игровом столе - бьет карта то, что там есть или нет (т.е. когда твой ход первый, результат всегда true)
 { if Player[FCurrPlayer].Difficulty = dfEasy then
  begin
    if FCurrStep = 0 then result := airUnknown;
    exit;
  end; }

  // 1. анализ карт на игровом столе (если твой ход первый - анализировать нечего)
  if FCurrStep > 0 then
  begin
    if (result = airPass) or (FCurrStep = 2) then exit;
  end else
    result := airUnknown;

  l := GetCardLear(Card);
  plNext := GetNextIndex(FCurrPlayer);
  //pl2 := GetNextIndex(pl1);

  // 2. анализ вышедших мастей
  pli := FCurrPlayer;
  for i := FCurrStep + 1 to 2 do
  begin
    pli := GetNextIndex(pli);

    case Player[FCurrPlayer].Difficulty of
      dfEasy:
      begin
        // просматриваем среди вышедших мастей у следующих за текущим игроков
        // если у игрока масть вышла
        if FindReleasedLear(l, pli) then
        begin
          // если у него вышли козыри (если козырь играет) - то он не бьет
          if FTrump = lnNone then result := airTake
          else begin
            if FindReleasedLear(FTrump, pli) then result := airTake
            else
              if (FDeals[FCurrDealNo].Deal in [dNoTrump, dDark, dGold, dMizer]) or ((FDeals[FCurrDealNo].Deal = dNormal) and
                ((FDeals[FCurrDealNo].CardCount = 12) or (FDeals[FCurrDealNo].CardCount = 17))) then
                result := airPass
              else
                result := airUnknown;
          end;
        end else
        begin
          result := airTake;

          // если масть осталась - проверим по вышедшим картам
          // пробежимся по всем картам, что крупнее проверяемой и поищем среди вышедших
          for j := Ord(Card) + 1 to EndLearCardOrd(l) do
          begin
            // если карта у себя - не смотрим
            if FindCard(TCard(j), Party[FCurrPlayer].Cards) then continue;

            // карта вышла - продолжаем поиск пока не наткнемся на НЕвышедшую
            if FindReleasedCard(TCard(j)) then result := airTake
            else begin
              // карты среди вышедших нет
              if FCurrStep > 0 then
              begin
                // если ход не первый, то попробуем понять, у кого осталась эта крупная карта (если у первого, то ок, продолжаем):
                // если у последнего закончилась эта масть, значит карта у первого - продолжаем; иначе карта может быть у любого - выход
                if FindReleasedLear(l, plNext) then result := airTake
                else result := airUnknown;
              end else
                if (FDeals[FCurrDealNo].Deal in [dNoTrump, dDark, dGold, dMizer]) or ((FDeals[FCurrDealNo].Deal = dNormal) and
                  ((FDeals[FCurrDealNo].CardCount = 12) or (FDeals[FCurrDealNo].CardCount = 17))) then
                  result := airPass
                else
                  result := airUnknown;
            end;

            if result <> airTake then break;
          end;
        end;
      end;
      dfNormal, dfHard:
      begin
        // просматриваем среди карт у следующих за текущим игроков
        // если у игрока масть вышла
        if not FindCardLear(l, Party[pli].Cards) then
        begin
          // если у него вышли козыри (если козырь играет) - то он не бьет
          if FTrump = lnNone then result := airTake
          else begin
            if not FindCardLear(FTrump, Party[pli].Cards) then result := airTake
            else result := airPass;
          end;
        end else
        begin
          result := airTake;

          for j := Ord(Card) + 1 to EndLearCardOrd(l) do
            if FindCard(TCard(j), Party[pli].Cards) then
            begin
              result := airPass;
              break;
            end;
        end;
      end;
    end;

    if result <> airTake then exit;
  end;
end;

function TCustomGame.AIGtdPass(pIdx: integer; Card: TCard): boolean;
var
  l: TLearName;
  i: integer;

begin
  // определяет, что данный игрок 100% скинет на эту карту в данный момент
  result := false;
  l := GetCardLear(Card);

  case Player[FCurrPlayer].Difficulty of
    dfEasy: // анализ по вышедшему
    begin
      // если масть у игрока вышла
      if FindReleasedLear(l, pIdx) then
      begin
        // если возможно бить козырем и козыри вышли, точно скинет
        if (FTrump <> lnNone) and (l <> FTrump) and FindReleasedLear(FTrump, pIdx) then result := true;
        exit;
      end;

      // если масть есть - посмотрим вышедшие карты. Если вышло все, что больше - то скинет точно
      for i := Ord(Card) + 1 to EndLearCardOrd(l) do
        if not FindReleasedCard(TCard(i)) then exit;

      result := true;
    end;
    dfNormal, dfHard: // анализ по картам игрока
    begin
      // масть вышла
      if not FindCardLear(l, Party[pIdx].Cards) then
      begin
        // если возможно бить козырем и козырей нет  - точно скинет
        if (FTrump <> lnNone) and (l <> FTrump) and (not FindCardLear(FTrump, Party[pIdx].Cards)) then result := true;
        exit;
      end;

      // если масть есть - посмотрим карты. Если вышло все, что больше - то точно скинет
      for i := Ord(Card) + 1 to EndLearCardOrd(l) do
        if FindCard(TCard(i), Party[pIdx].Cards) then exit;

      result := true;
    end;
  end;
end;

function TCustomGame.AIGtdTake(pIdx: integer; Card: TCard): boolean;
var
  l: TLearName;
  i: integer;

begin
  // определяет, что данный игрок 100% побъет эту карту в данный момент
  result := false;
  l := GetCardLear(Card);

  case Player[FCurrPlayer].Difficulty of
    dfEasy: // анализ по вышедшему
    begin
      // если масть у игрока вышла
      if FindReleasedLear(l, pIdx) then
      begin
        // если возможно бить козырем и козыри есть - точно побьет
        if (FTrump <> lnNone) and (l <> FTrump) and (not FindReleasedLear(FTrump, pIdx)) then result := true;
        exit;
      end;

      // если масть есть - посмотрим вышедшие карты. Если вышло все, что меньше - то побьет точно
      // пробежимся по всем картам, что меньше проверяемой и поищем
      for i := StartLearCardOrd(l) to Ord(Card) - 1 do
        if not FindReleasedCard(TCard(i)) then exit;

      result := true;
    end;
    dfNormal, dfHard: // анализ по картам игрока
    begin
      // масть вышла
      if not FindCardLear(l, Party[pIdx].Cards) then
      begin
        // если возможно бить козырем и козыри есть - точно побьет
        if (FTrump <> lnNone) and (l <> FTrump) and FindCardLear(FTrump, Party[pIdx].Cards) then result := true;
        exit;
      end;

      // если масть есть - посмотрим карты. Если вышло все, что меньше - то побьет точно
      // пробежимся по всем картам, что меньше проверяемой и поищем
      for i := StartLearCardOrd(l) to Ord(Card) - 1 do
        if FindCard(TCard(i), Party[pIdx].Cards) then exit;

      result := true;
    end;
  end;
end;

function TCustomGame.IndexOfCard(Card: TCard; Cards: TCards; Offset: integer): integer;
var
  i: integer;

begin
  // индекс карты Card в массиве
  result := -1;
  for i := Offset to Length(Cards) - 1 do
    if Cards[i] = Card then
    begin
      result := i;
      exit;
    end;
end;

function TCustomGame.IndexOfCardLear(Lear: TLearName; Cards: TCards): integer;
var
  i: integer;

begin
  // индекс первой карты указанной масти
  result := -1;
  for i := 0 to Length(Cards) - 1 do
    if GetCardLear(Cards[i]) = Lear then
    begin
      result := i;
      exit;
    end;
end;

procedure TCustomGame.InitializeGameData(CanFreeParty: boolean);
begin
  FCurrDealNo := -1;
  FCurrPlayer := -1;
  FCurrStep := -1;
  OldStep := -1;
  FCanStopGame := false;
  
  if Assigned(StatTable) then
  begin
    if StatTable.Active then StatTable.EmptyTable;
    StatTable.Close;
    StatTable.CreateDataSet;
  end;

  if CanFreeParty then ClearParty
  else InitPlayers;

  SetLength(FTable, 0);
  SetLength(FDeals, 0);
  SetLength(FReleasedCards, 0);
  SetLength(FReleasedLears, 0);
end;

procedure TCustomGame.InitPlayers;
var
  i: integer;

begin
  for i := 0 to Length(Party) - 1 do
  begin
    Party[i].Order := -1;
    Party[i].Take := -1;
    Party[i].Scores := 0;
    SetLength(Party[i].Cards, 0);
    SetLength(Party[i].OrderCards, 0);
  end;
end;

function TCustomGame.LearToStr(l: TLearName; NoTrumpStr: string; Short: boolean): string;
begin
  case l of
    lnHearts: result := iif(Short, 'Ч', 'Черва');
    lnDiamonds: result := iif(Short, 'Б', 'Бубна');
    lnClubs: result := iif(Short, 'К', 'Крестя');
    lnSpades: result := iif(Short, 'П', 'Пика');
    lnNone: result := NoTrumpStr;
  end;
end;

function TCustomGame.LoadGame(PlayerId: string): boolean;
var
  fs: TFileStream;
  ss: TStringStream;
  h: TSaveFileHeader;
  d: TSaveFileData;
  p: TSaveFilePartyPlayer;
  i, j: integer;
  sl: TStringList;
  fn, s, log: string;
  l: TMsgLabel;

begin
  result := false;
  fn := DataDir + Format(SAVE_FILE, [PlayerId]);
  if not FileExists(fn) then exit;

  try
    try
      sl := TStringList.Create;
      ss := TStringStream.Create('');
      fs := TFileStream.Create(fn, fmOpenRead);
      fs.Seek(0, soFromBeginning);

      // читаем заголовок
      fs.Read(h, SizeOf(TSaveFileHeader));

      // читаем данные игры
      fs.Read(d, SizeOf(TSaveFileData));
      FCurrDealNo := d.CurrDealNo;
      FCurrPlayer := d.CurrPlayer;
      FTrump := d.Trump;
      FCurrStep := d.CurrStep;
      FBet := d.Bet;
      CanNextDeal := d.CanNextDeal;
      FCanStopGame := d.CanStopGame;
      OldStep := d.OldStep;
      FNoWalk := d.NoWalk;
      TakePlayer := d.TakePlayer;
      noPause := d.noPause;
      Deck := d.Deck;
      GameOptions := d.GameOptions;
      NoJoker := d.NoJoker;
      StrongJoker := d.StrongJoker;
      JokerMajorLear := d.JokerMajorLear;
      JokerMinorLear := d.JokerMinorLear;
      MultDark := d.MultDark;
      MultBrow := d.MultBrow;
      PassPoints := d.PassPoints;
      LongGame := d.LongGame;
      CanPause := d.CanPause;
      PenaltyMode := d.PenaltyMode;

      // читаем динамические данные
      // раздачи
      SetLength(FDeals, h.szDeals);
      for i := 0 to h.szDeals - 1 do fs.Read(FDeals[i], SizeOf(TDeal));
      // массив вышедших карт
      SetLength(FReleasedCards, h.szReleasedCards);
      for i := 0 to h.szReleasedCards - 1 do fs.Read(FReleasedCards[i], SizeOf(TReleasedCard));
      // массив вышедших мастей
      SetLength(FReleasedLears, h.szReleasedLears);
      for i := 0 to h.szReleasedLears - 1 do fs.Read(FReleasedLears[i], SizeOf(TReleasedLear));
      // таблица игры
      if Assigned(StatTable) then
      begin
        if StatTable.Active then StatTable.EmptyTable;
        StatTable.Close;
        StatTable.CreateDataSet;
      end;
      ss.CopyFrom(fs, h.szStatTable);
      ss.Seek(0, soFromBeginning);
      sl.LoadFromStream(ss);
      StatTable.DisableControls;
      for i := 0 to sl.Count - 1 do
      begin
        StatTable.Append;
        StatTable.FieldByName('ID').AsString := Trim(ExtractWordEx(1, sl.Strings[i], [REC_WORD_DELIM], []));
        StatTable.FieldByName('DEAL_NO').AsString := Trim(ExtractWordEx(2, sl.Strings[i], [REC_WORD_DELIM], []));
        StatTable.FieldByName('DEAL_NAME').AsString := ExtractWordEx(3, sl.Strings[i], [REC_WORD_DELIM], []);
        StatTable.FieldByName('P0ORDER').AsString := ExtractWordEx(4, sl.Strings[i], [REC_WORD_DELIM], []);
        StatTable.FieldByName('P0TAKE').AsString := ExtractWordEx(5, sl.Strings[i], [REC_WORD_DELIM], []);
        StatTable.FieldByName('P0POINTS').AsString := Trim(ExtractWordEx(6, sl.Strings[i], [REC_WORD_DELIM], []));
        StatTable.FieldByName('P1ORDER').AsString := ExtractWordEx(7, sl.Strings[i], [REC_WORD_DELIM], []);
        StatTable.FieldByName('P1TAKE').AsString := ExtractWordEx(8, sl.Strings[i], [REC_WORD_DELIM], []);
        StatTable.FieldByName('P1POINTS').AsString := Trim(ExtractWordEx(9, sl.Strings[i], [REC_WORD_DELIM], []));
        StatTable.FieldByName('P2ORDER').AsString := ExtractWordEx(10, sl.Strings[i], [REC_WORD_DELIM], []);
        StatTable.FieldByName('P2TAKE').AsString := ExtractWordEx(11, sl.Strings[i], [REC_WORD_DELIM], []);
        StatTable.FieldByName('P2POINTS').AsString := Trim(ExtractWordEx(12, sl.Strings[i], [REC_WORD_DELIM], []));
        StatTable.Post;
      end;
      StatTable.Locate('ID', GetCurrId, []);

      // игровой стол
      SetLength(FTable, h.szTable);
      for i := 0 to h.szTable - 1 do fs.Read(FTable[i], SizeOf(TTable));
      // игроки партии
      for i := 0 to Length(Party) - 1 do
      begin
        fs.Read(p, SizeOf(TSaveFilePartyPlayer));
        Party[i].Index := FindPlayerById(p.Id, Players);
        if ((Party[i].Index < 0) or (Party[i].Index >= Length(Players))) or
          ((i < 2) and (Player[i].Control = ctHumanLocal)) or
          ((i = 2) and (Player[i].Control <> ctHumanLocal)) then
          raise Exception.Create('Поврежден список игроков партии! Продолжить игру невозможно.');
          
        Party[i].Order := p.Order;
        Party[i].Take := p.Take;
        Party[i].Scores := p.Scores;
        Party[i].Total := p.Total;
        SetLength(Party[i].Cards, p.szCards);
        for j := 0 to p.szCards - 1 do fs.Read(Party[i].Cards[j], SizeOf(TCard));
        SetLength(Party[i].OrderCards, p.szOrderCards);
        for j := 0 to p.szOrderCards - 1 do fs.Read(Party[i].OrderCards[j], SizeOf(TCard));
      end;

      // теперь запускаем игру
      Randomize;
      GameTime := Now - h.GameTime;
      // размер колоды
      case Deck of
        dsz36: DeckSz := 36;
        dsz54:
          if NoJoker then DeckSz := 51
          else DeckSz := 54;
      end;

      if FCanStopGame then
      begin
        // конец игры - на всякий случай, если вдруг окажется сохранено состояние конца игры
        FStarted := true;
        StopGame(true);
        exit;
      end;
      prevDeal := FDeals[FCurrDealNo].Deal;
      FStarted := true;
      result := true;
      if Assigned(FDrawProc) then FDrawProc(true);
      if Assigned(FSetMsgProc) then
      begin
        FSetMsgProc(lDeal, 'Раздача: ' + DealToStr(FDeals[FCurrDealNo], true) + '. Первый ход: ' +
          Player[FDeals[FCurrDealNo].Player].Name, 0, true, false);
          
        for i := 0 to Length(Party) - 1 do
        begin
          if Party[i].Order = 0 then s := 'Пас'
          else if Party[i].Order < 0 then s := ''
          else s := 'Мой заказ: ' + IntToStr(Party[i].Order);

          case i of
            0: l := lP1Order;
            1: l := lP2Order;
            2: l := lP3Order;
          end;
          FSetMsgProc(l, s, 0, false, false);

          if Party[i].Take > 0 then
          begin
            case i of
              0: l := lP1Take;
              1: l := lP2Take;
              2: l := lP3Take;
            end;
            FSetMsgProc(l, 'Взял: ' + IntToStr(Party[i].Take), 0, false, false);
          end;

          if KeepLog then
            if log = '' then log := Player[i].Name
            else log := log + ', ' + Player[i].Name;
        end;
      end;

      if KeepLog then
      begin
       // if FileExists(DataDir + LOG_FILE) then DeleteFile(DataDir + LOG_FILE);
        AddToLog(DataDir + LOG_FILE, '*****************************************************'#13#10 +
          'Загружена игра.'#13#10'Игроки: ' + log, 0);

        log := #13#10'Раздача: ' + DealToStr(FDeals[FCurrDealNo], true) + '. Козырь: ' + LearToStr(FTrump, 'нет') +
          '. Первый ход: ' + Player[FCurrPlayer].Name;

        for i := 0 to Length(Party) - 1 do
        begin
          log := log + #13#10 + Player[i].Name + ':';
          for j := 0 to Length(Party[i].Cards) - 1 do
            log := log + ' ' + CardToStr(Party[i].Cards[j], true, true);
        end;

        AddToLog(DataDir + LOG_FILE, log, Now - GameTime);
      end;
    finally
      StatTable.EnableControls;
      ss.Free;
      sl.Free;
      if Assigned(fs) then fs.Free;
      if result then Next
      else if FileExists(fn) then DeleteFile(fn);
    end;
  except
    // если произошли ошибки при загрузке - файл не валидный или не актуален - удаляем его и запуск новой игры
    on e: Exception do
    begin
      if FileExists(fn) then DeleteFile(fn);
      Application.MessageBox(pchar(e.Message), 'Ошибка', MB_OK + MB_ICONERROR);
    end;
  end;
end;

function TCustomGame.LoadPlayers: boolean;
var
  fs: TFileStream;
  h: TPlayerDataFileHeader;
  i: integer;

begin
  result := false;
  SetLength(Players, 0);
  if not FileExists(DataDir + PLAYER_DATA_FILE) then exit;

  try
    h.pCount := 0;
    fs := TFileStream.Create(DataDir + PLAYER_DATA_FILE, fmOpenRead);
    fs.Seek(0, soFromBeginning);
    fs.Read(h, SizeOf(TPlayerDataFileHeader));

    for i := 0 to h.pCount - 1 do
    begin
      SetLength(Players, i + 1);
      fs.Read(Players[i], SizeOf(TPlayer));
      if Players[i].Password <> '' then Players[i].Password := DCS_(Players[i].Password);
    end;
    result := true;
  finally
    if Assigned(fs) then fs.Free;
  end;
end;

procedure TCustomGame.Next(canRefresh: boolean);
var
  e: string;
  ja: TJokerAction;
  jc: TCard;
  ci: integer;
  
begin
  FNoWalk := false;
  if FCanStopGame then
  begin
    //StopGame(true);
    exit;
  end;

  if CanNextDeal then
  begin
    if CanPause then
    begin
      CanPause := false;
      FSetPlayerConProc(1);
      CalcStatistic;
      exit;
    end;
    EndRound;
    DealCards;
    Next; //(false);
    exit;
  end;

  if (not FBet) and (OldStep = 2) and (not noPause) {and Player[FCurrPlayer].Robot} then
  begin
    // все походили, надо очистить стол и сделать паузу
    OldStep := -1;
    FNoWalk := true;
    if canRefresh and Assigned(FDrawProc) then FDrawProc(false);
    SetLength(FTable, 0);
    FSetPlayerConProc(1);
    exit;
  end;
  noPause := false;
  
  if Assigned(FSetMsgProc) then
  begin
    if FBet then
      FSetMsgProc(lInfo, 'Заказывает ' + Player[FCurrPlayer].Name, iif(Player[FCurrPlayer].Control = ctRobot, WaitDelay, 0), false, false)
    else
      FSetMsgProc(lInfo, 'Ходит ' + Player[FCurrPlayer].Name, iif(Player[FCurrPlayer].Control = ctRobot, WaitDelay, 0), false, false);
  end;

  // передача управления игроку
  if Player[FCurrPlayer].Control = ctHumanLocal then
  begin
    if Assigned(FSetPlayerConProc) then
    begin
      if FBet then FSetPlayerConProc(0)
      else FSetPlayerConProc(-1);
    end;
    if canRefresh and Assigned(FDrawProc) then FDrawProc(false);
    exit;
  end;

  Screen.Cursor := crHourGlass;
  try
    if FBet then
    begin
      // делаем ставки
      while not MakeOrder(FCurrPlayer, AICalcOrder, e) do ;
      GiveWalk;
    end else
    begin
      // ходим
      if FCurrStep = 0 then
      begin
        ci := AICalcWalk(ja, jc);
        while not DoWalk(FCurrPlayer, ci, ja, jc, e) do ci := AICalcWalk(ja, jc);
      end else
      begin
        ci := AICalcBeat(ja, jc);
        while not DoBeat(FCurrPlayer, ci, ja, jc, e) do ci := AICalcBeat(ja, jc, true);
      end;
      GiveWalk;
    end;
  finally
    Screen.Cursor := crDefault;
  end;
  if canRefresh and Assigned(FDrawProc) then FDrawProc(false);
  Next; //(false);
end;

function TCustomGame.MakeOrder(pIdx, Order: integer; var Err: string): boolean;
var
  msg, log: string;
  l: TMsgLabel;
  i, x: integer;

begin
  Err := '';
  result := false;

  if (Order < 0) then Err := 'Неверный заказ (' + IntToStr(Order) + ')!';
  if (Order > FDeals[FCurrDealNo].CardCount) then Err := 'Заказ не может превышать количество карт в раздаче!';

  if FCurrStep = 2 then
  begin
    x := Order;
    for i := 0 to Length(Party) - 1 do if i <> FCurrPlayer then x := x + Party[i].Order;

    if FDeals[FCurrDealNo].CardCount = x then
      Err := 'Сумма заказов всех игроков не может быть равна количеству карт в раздаче!';
  end;

  if Err <> '' then exit;

  if Order = 0 then msg := 'Пас'
  else msg := 'Мой заказ: ' + IntToStr(Order);

  case pIdx of
    0: l := lP1Order;
    1: l := lP2Order;
    2: l := lP3Order;
  end;
  if Assigned(FSetMsgProc) then FSetMsgProc(l, msg, 0, false, false);
  Party[pIdx].Order := Order;
  CopyStat(GetCurrId);

  // лог
  if KeepLog then
  begin
    log := IntToStr(pIdx + 1) + '.' + Player[pIdx].Name + ' - заказ: ' + IntToStr(Party[pIdx].Order);
    AddToLog(DataDir + LOG_FILE, log, Now - GameTime);
  end;

  result := true;
end;

function TCustomGame.DoBeat(pIdx, CardIndex: integer; JokerAction: TJokerAction; JokerCard: TCard; var Err: string): boolean;
var
  c: TCard;
  l, tl: TLearName;
  maxCard, minCard: TCard;
  lb: TMsgLabel;
  i: integer;
  log: string;
  
begin
  Err := '';
  TakePlayer := -1;
  result := false;

  if (pIdx < 0) or (pIdx >= Length(Party)) then
    raise Exception.Create('Индекс игрока вышел за границы массива!');
  if Length(FTable) = 3 then raise Exception.Create('Все уже походили!');

  if (CardIndex < 0) or (CardIndex >= Length(Party[pIdx].Cards)) then
  begin
    // raise Exception.Create('Индекс карты вышел за границы массива!');
    Err := 'Индекс карты вышел за границы массива!';
    exit;
  end;

  // сначала проверить, можно ли ходить этой картой
  if (Party[pIdx].Cards[CardIndex] in [cJoker1, cJoker2]) then
  begin
    c := JokerCard;
    l := GetCardLear(JokerCard);
  end else
  begin
    c := Party[pIdx].Cards[CardIndex];
    l := GetCardLear(c);
  end;

  if (FTable[0].Card in [cJoker1, cJoker2]) then
    tl := GetCardLear(FTable[0].JokerCard)
  else
    tl := GetCardLear(FTable[0].Card);

  // если ты ходишь не джокером и первый ход сделан джокером, проверим требование по старшей/младшей карте масти
  if (not (Party[pIdx].Cards[CardIndex] in [cJoker1, cJoker2])) and (FTable[0].Card in [cJoker1, cJoker2]) then
  begin
    case FTable[0].JokerAction of
      jaByMax:
        if FindCardLear(tl, Party[pIdx].Cards) and (GetMaxCard(tl, Party[pIdx].Cards) <> c) then
        begin
          Err := 'Вы вы обязаны кинуть самую крупную ' + LearToStr(tl, '') + '.';
          exit;
        end;
      jaByMin:
        if FindCardLear(tl, Party[pIdx].Cards) and (GetMinCard(tl, Party[pIdx].Cards) <> c) then
        begin
          Err := 'Вы вы обязаны кинуть самую маленькую ' + LearToStr(tl, '') + '.';
          exit;
        end;
    end;
  end;

  // если кинул джокера, то проверка чуток другая
  if (Party[pIdx].Cards[CardIndex] in [cJoker1, cJoker2]) then
  begin
    if (l <> tl) then
    begin
      if StrongJoker then
      begin
        Err := 'Вы можете выдать Джокера только за ту масть, которой был сделан ход (' + LearToStr(tl, '') + ').';
        exit;
      end else
        if (l <> FTrump) then
        begin
          Err := 'Вы обязаны ходить Джокером или по масти или как козырем.';
          exit;
        end;
    end;
  end else
  begin
    // если есть масть, то обязан ходить этой мастью
    if FindCardLear(tl, Party[pIdx].Cards) then
    begin
      if (l <> tl) then
      begin
        Err := 'Вы можете ходить только той мастью, которой был сделан ход (' + LearToStr(tl, '') + ').';
        exit;
      end;
    end else
    begin
      // если масти нет, но есть козырь, то обязан ходить козырем (если не ходил джокером)
      if (FTrump <> lnNone) and (l <> FTrump) and FindCardLear(FTrump, Party[pIdx].Cards) then
      begin
        Err := 'Если у вас нет нужной масти, но есть козырь - вы обязаны ходить козырем.';
        exit;
      end;
    end;
  end;

  // проверить, если по логике хода масть закончилась, то записать ее в массив вышедших мастей, если ее там нет
  if (not (Party[pIdx].Cards[CardIndex] in [cJoker1, cJoker2])) and (l <> tl) then AddReleasedLear(l, pIdx);

  result := DoWalk(pIdx, CardIndex, JokerAction, JokerCard, Err);
  if not result then exit;
  if FCurrStep < 2 then exit;

  // определяем, кто побил
  if FTable[0].Card in [cJoker1, cJoker2] then maxCard := FTable[0].JokerCard
  else maxCard := FTable[0].Card;
  TakePlayer := FTable[0].Player;

  for i := 1 to 2 do
  begin
    if FTable[i].Card in [cJoker1, cJoker2] then minCard := FTable[i].JokerCard
    else minCard := FTable[i].Card;

    if (GetCardLear(maxCard) = GetCardLear(minCard)) then
    begin
      if (maxCard = minCard) then
      begin
        if (FTable[i].Card in [cJoker1, cJoker2]) and
          (not (ChangeCardLear(FTable[i].JokerCard, lnHearts) in [ch2, ch6])) then TakePlayer := FTable[i].Player;
      end else
      begin
        maxCard := TCard(Max(Ord(maxCard), Ord(minCard)));
        if FTable[i].Card in [cJoker1, cJoker2] then
          TakePlayer := iif(maxCard = FTable[i].JokerCard, FTable[i].Player, TakePlayer)
        else
          TakePlayer := iif(maxCard = FTable[i].Card, FTable[i].Player, TakePlayer);
      end;
    end else if (GetCardLear(minCard) = FTrump) then
    begin
      maxCard := minCard;
      TakePlayer := FTable[i].Player;
    end;
  end;

  // записываем в статистику
  Inc(Party[TakePlayer].Take);
  if Assigned(FSetMsgProc) then
  begin
    case TakePlayer of
      0: lb := lP1Take;
      1: lb := lP2Take;
      2: lb := lP3Take;
    end;
    FSetMsgProc(lInfo, 'Взял: ' + Player[TakePlayer].Name + ' - ' + CardToStr(maxCard), 0, false, false);
    FSetMsgProc(lb, 'Взял: ' + IntToStr(Party[TakePlayer].Take), 0, false, false);
  end;

  if KeepLog then
  begin
    for i := 0 to Length(FTable) - 1 do
    begin
      if log <> '' then log := log + ', ';
      log := log + IntToStr(FTable[i].Player + 1) + '.' + Player[FTable[i].Player].Name + ' - ' + CardToStr(FTable[i].Card);

      if FTable[i].Card in [cJoker1, cJoker2] then
        log := log + ': ' + JokerActionToStr(FTable[i].JokerAction, FTable[i].JokerCard);
    end;

    log := log + #13#10'Взял: ' + Player[TakePlayer].Name + ' - ' + CardToStr(maxCard);
    AddToLog(DataDir + LOG_FILE, log, Now - GameTime);
  end;

  CopyStat(GetCurrId);
  result := true;
end;

function TCustomGame.DoWalk(pIdx, CardIndex: integer; JokerAction: TJokerAction; JokerCard: TCard; var Err: string): boolean;
begin
  Err := '';
  TakePlayer := -1;
  result := false;

  if (pIdx < 0) or (pIdx >= Length(Party)) then
    raise Exception.Create('Индекс игрока вышел за границы массива!');
  if Length(FTable) = 3 then raise Exception.Create('Все уже походили!');

  if (CardIndex < 0) or (CardIndex >= Length(Party[pIdx].Cards)) then
  begin
    //raise Exception.Create('Индекс карты вышел за границы массива!');
    Err := 'Ошибка! Индекс карты вышел за границы массива!';
    exit;
  end;

  if (pIdx <> 2) and (Party[pIdx].Cards[CardIndex] in [cJoker1, cJoker2]) then
    Application.MessageBox(pchar('Хожу Джокером!'#13#10 + JokerActionToStr(JokerAction, JokerCard)),
      pchar(string(Player[pIdx].Name)), MB_OK + MB_ICONINFORMATION);

  // запомнить карту в массиве вышедших карт (если ее там еще нет)
  AddReleasedCard(Party[pIdx].Cards[CardIndex], pIdx);

  // перекинуть карту из массива игрока в массив стола
  SetLength(FTable, Length(FTable) + 1);
  FTable[High(FTable)].Player := pIdx;
  FTable[High(FTable)].Card := Party[pIdx].Cards[CardIndex];
  FTable[High(FTable)].JokerAction := JokerAction;
  FTable[High(FTable)].JokerCard := JokerCard;
  DelOrderCard(pIdx, IndexOfCard(Party[pIdx].Cards[CardIndex], Party[pIdx].OrderCards));
  DelCard(pIdx, CardIndex);
  if Party[pIdx].Take < 0 then Party[pIdx].Take := 0;

  result := true;
end;

procedure TCustomGame.EndGame;
var
  i, wi, x: integer;
  winText, log, s: string;
  l: TMsgLabel;
  maxs, mids, mins: integer;
  maxi, midi, mini: integer;

begin
  FCanStopGame := true;
  if Assigned(FSetMsgProc) then FSetMsgProc(lDeal, 'Игра закончена', 0, true, false);

  // определяем победителя, расчитываем и записываем выигрыш и статистику
  maxs := -MaxInt;
  mids := 0;
  mins := MaxInt;
  for i := 0 to Length(Party) - 1 do
  begin
    if maxs < Party[i].Total then
    begin
      maxs := Party[i].Total;
      maxi := i;
    end;
    if mins > Party[i].Total then
    begin
      mins := Party[i].Total;
      mini := i;
    end;
  end;

  for i := 0 to Length(Party) - 1 do
    if (i <> maxi) and (i <> mini) then
    begin
      mids := Party[i].Total;
      midi := i;
      break;
    end;

  // выигравший получает с каждого разницу между своими очками и очками каждого из игроков
  Inc(Players[Party[maxi].Index].cScores, (maxs - mids) + (maxs - mins));
  // Считаем потери (выигрыш) второго: с проигравшего получает разницу между свими очками и очками проигравшего.
  // Вычитаем полученное из того, что он отдает выигравшему, получаем сумму потерь.
  // Т.к. это потери, то меняем знак, хотя в итоге тут может оказаться и выигрыш, если сумма потреь будет со знаком минус
  Inc(Players[Party[midi].Index].cScores, -((maxs - mids) - (mids - mins)));
  // потери проигравшего: то что он отдал выигравшему (разница между свими очками и очками выигравшего) +
  // то, что отдал второму (разница между очками второго и своими). Все со знаком минус
  Inc(Players[Party[mini].Index].cScores, -((maxs - mins) + (mids - mins)));

  // определяем победителя
  //maxs := Max(Party[0].Total, Max(Party[1].Total, Party[2].Total));
  wi := -1;
  for i := 0 to Length(Party) - 1 do
  begin
    Inc(Players[Party[i].Index].cTotal, Party[i].Total);
    Inc(Players[Party[i].Index].cCompleted);

    if Party[i].Total = maxs then
    begin
      Inc(Players[Party[i].Index].cWinned);
      x := (maxs - mids) + (maxs - mins);
      s := 'выигрыш ' + IntToStr(x);

      if wi = -1 then
      begin
        wi := i;
        winText := 'Выиграл ' + Player[i].Name;
      end else
        winText := 'Ничья';
    end else
    if Party[i].Total = mids then
    begin
      Inc(Players[Party[i].Index].cFailed);
      x := -((maxs - mids) - (mids - mins));
      s := iif(x < 0, 'проигрыш ', 'выигрыш ') + IntToStr(x);
    end else
    if Party[i].Total = mins then
    begin
      Inc(Players[Party[i].Index].cFailed);
      x := -((maxs - mins) + (mids - mins));
      s := 'проигрыш ' + IntToStr(x);
    end;

    case i of
      0: l := lP1Order;
      1: l := lP2Order;
      2: l := lP3Order;
    end;
    if Assigned(FSetMsgProc) then FSetMsgProc(l, 'Счет: ' + IntToStr(Party[i].Total) + ', ' + s, 0, false, false);
    if KeepLog then
      log := log + IntToStr(i + 1) + '.' + Player[i].Name + ' - счет: ' + IntToStr(Party[i].Total) + ', ' + s + #13#10;
  end;

  if Assigned(FSetMsgProc) then FSetMsgProc(lInfo, winText, 0, false, true);
  if Assigned(FSetPlayerConProc) then FSetPlayerConProc(2);

  if FileExists(DataDir + Format(SAVE_FILE, [Player[2].Id])) then
    DeleteFile(DataDir + Format(SAVE_FILE, [Player[2].Id]));
  
  if KeepLog then
    AddToLog(DataDir + LOG_FILE, winText + #13#10 + log, Now - GameTime);
end;

function TCustomGame.EndLearCardOrd(Lear: TLearName): integer;
begin
  case Lear of
    lnHearts: result := 12;
    lnDiamonds: result := 25;
    lnClubs: result := 38;
    lnSpades: result := 51;
  end;
end;

procedure TCustomGame.EndRound;
begin
  SetLength(FTable, 0);
  SetLength(FReleasedCards, 0);
  SetLength(FReleasedLears, 0);
  InitPlayers;
  if Assigned(FDrawProc) then FDrawProc(false);
end;

procedure TCustomGame.SaveGame;
var
  fs: TFileStream;
  h: TSaveFileHeader;
  d: TSaveFileData;
  p: TSaveFilePartyPlayer;
  i, j: integer;
  sl: TStringList;
  fn: string;

begin
  if FCanStopGame then exit; // это уже конец игры - сохранять не надо  

  try
    try
      fn := DataDir + Format(SAVE_FILE, [Player[2].Id]);
      sl := TStringList.Create;
      fs := TFileStream.Create(fn, fmCreate);
      fs.Seek(0, soFromBeginning);

      // подготовим данные таблицы игры к записи
      StatTable.DisableControls;
      StatTable.First;
      while not StatTable.Eof do
      begin
        sl.Add(StatTable.FieldByName('ID').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('DEAL_NO').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('DEAL_NAME').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('P0ORDER').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('P0TAKE').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('P0POINTS').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('P1ORDER').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('P1TAKE').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('P1POINTS').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('P2ORDER').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('P2TAKE').AsString + REC_WORD_DELIM +
          StatTable.FieldByName('P2POINTS').AsString + REC_WORD_DELIM);
        StatTable.Next;
      end;
      StatTable.Locate('ID', GetCurrId, []);

      // пишем заголовок
      //GameTime := Now - GameTime;
      h.GameTime := Now - GameTime;
      h.szDeals := Length(FDeals);
      h.szStatTable := Length(sl.Text);
      h.szTable := Length(FTable);
      h.szReleasedCards := Length(FReleasedCards);
      h.szReleasedLears := Length(FReleasedLears);
      fs.Write(h, SizeOf(TSaveFileHeader));

      // пишем данные игры
      d.CurrDealNo := FCurrDealNo;
      d.CurrPlayer := FCurrPlayer;
      d.Trump := FTrump;
      d.CurrStep := FCurrStep;
      d.Bet := FBet;
      d.CanNextDeal := CanNextDeal;
      d.CanStopGame := FCanStopGame;
      d.OldStep := OldStep;
      d.NoWalk := FNoWalk;
      d.TakePlayer := TakePlayer;
      d.noPause := noPause;
      d.Deck := Deck;
      d.GameOptions := GameOptions;
      d.NoJoker := NoJoker;
      d.StrongJoker := StrongJoker;
      d.JokerMajorLear := JokerMajorLear;
      d.JokerMinorLear := JokerMinorLear;
      d.MultDark := MultDark;
      d.MultBrow := MultBrow;
      d.PassPoints := PassPoints;
      d.LongGame := LongGame;
      d.CanPause := CanPause;
      d.PenaltyMode := PenaltyMode;
      fs.Write(d, SizeOf(TSaveFileData));

      // пишем динамические данные
      // раздачи
      for i := 0 to h.szDeals - 1 do fs.Write(FDeals[i], SizeOf(TDeal));
      // вышедшие карты
      for i := 0 to h.szReleasedCards - 1 do fs.Write(FReleasedCards[i], SizeOf(TReleasedCard));
      // вышедшие масти
      for i := 0 to h.szReleasedLears - 1 do fs.Write(FReleasedLears[i], SizeOf(TReleasedLear));
      // таблица игры
      sl.SaveToStream(fs);
      // игровой стол
      for i := 0 to h.szTable - 1 do fs.Write(FTable[i], SizeOf(TTable));
      // игроки партии
      for i := 0 to Length(Party) - 1 do
      begin
        p.Id := Player[i].Id;
        p.Order := Party[i].Order;
        p.Take := Party[i].Take;
        p.Scores := Party[i].Scores;
        p.Total := Party[i].Total;
        p.szCards := Length(Party[i].Cards);
        p.szOrderCards := Length(Party[i].OrderCards);
        fs.Write(p, SizeOf(TSaveFilePartyPlayer));
        for j := 0 to p.szCards - 1 do fs.Write(Party[i].Cards[j], SizeOf(TCard));
        for j := 0 to p.szOrderCards - 1 do fs.Write(Party[i].OrderCards[j], SizeOf(TCard));
      end;
    finally
      StatTable.EnableControls;
      sl.Free;
      if Assigned(fs) then fs.Free;
    end;
  except
    on e: Exception do
    begin
      // файл сохранения битый - грохаем его
      if FileExists(fn) then DeleteFile(fn);
      Application.MessageBox(pchar(e.Message), 'Ошибка', MB_OK + MB_ICONERROR);
    end;
  end;
end;

function TCustomGame.SavePlayers: boolean;
var
  fs: TFileStream;
  h: TPlayerDataFileHeader;
  i: integer;
  oldPwd: string;

begin
  result := false;
  try
    h.pCount := Length(Players);
    fs := TFileStream.Create(DataDir + PLAYER_DATA_FILE, fmCreate);
    fs.Seek(0, soFromBeginning);
    fs.Write(h, SizeOf(TPlayerDataFileHeader));

    for i := 0 to h.pCount - 1 do
    begin
      oldPwd := '';
      if Players[i].Password <> '' then
      begin
        oldPwd := Players[i].Password;
        Players[i].Password := ECS_(Players[i].Password);
      end;
      fs.Write(Players[i], SizeOf(TPlayer));
      if Players[i].Password <> '' then Players[i].Password := oldPwd;
    end;
    result := true;
  finally
    if Assigned(fs) then fs.Free;
  end;
end;

procedure TCustomGame.SetGameType(const Value: TGameType);
begin
  FGameType := Value;
end;

procedure TCustomGame.SetLearOrder(Value: TLearOrder);
var
  i: integer;

begin
  FLearOrder := Value;
  if FStarted and (FSortDirect in [sdAsc, sdDesc]) then
    for i := 0 to Length(Party) - 1 do SortPlayerCards(i);
end;

procedure TCustomGame.SetSortDirect(Value: TSortDirection);
var
  i: integer;

begin
  FSortDirect := Value;
  if FStarted and (FSortDirect in [sdAsc, sdDesc]) then
    for i := 0 to Length(Party) - 1 do SortPlayerCards(i);
end;

procedure TCustomGame.SkipDeal;
begin
  CalcStatistic(true);
  EndRound;
  DealCards;
  FCurrStep := 0;
  Next;
end;

procedure TCustomGame.SortPlayerCards(pIdx: integer);

  procedure Exchange(var arr: TCards; idx1, idx2: integer);
  var
    tmp: TCard;

  begin
    if (idx1 < 0) or (idx1 >= Length(arr)) then exit;
    if (idx2 < 0) or (idx2 >= Length(arr)) then exit;
    if idx1 = idx2 then exit;

    tmp := arr[idx1];
    arr[idx1] := arr[idx2];
    arr[idx2] := tmp;
  end;

  procedure Exchange2(var arr1, arr2: TCards; idx1, idx2: integer);
  var
    tmp: TCard;

  begin
    if (idx1 < 0) or (idx1 >= Length(arr1)) then exit;
    if (idx2 < 0) or (idx2 >= Length(arr2)) then exit;

    tmp := arr1[idx1];
    arr1[idx1] := arr2[idx2];
    arr2[idx2] := tmp;
  end;

var
  i, j, il: integer;
  arr: TCards;
  f: boolean;

begin
  if Length(Party[pIdx].Cards) < 2 then exit;
  if SortDirect = sdNone then exit;

  // сначала расположим все карты по возрастанию (убыванию) - сортировка выбором элемента
  for i := 0 to Length(Party[pIdx].Cards) - 2 do
  begin
    il := i;
    for j := i + 1 to Length(Party[pIdx].Cards) - 1 do
      if SortDirect = sdAsc then
      begin
        if Party[pIdx].Cards[il] > Party[pIdx].Cards[j] then il := j;
      end else
        if Party[pIdx].Cards[il] < Party[pIdx].Cards[j] then il := j;

    Exchange(Party[pIdx].Cards, il, i);
  end;

  // потом просто переставим масти в нужном порядке (массив уже отсортирован)
  SetLength(arr, 0);
  for i := 0 to Length(LearOrder) - 1 do
  begin
    f := false;
    for j := 0 to Length(Party[pIdx].Cards) - 1 do
      if GetCardLear(Party[pIdx].Cards[j]) = LearOrder[i] then
      begin
        f := true;
        SetLength(arr, Length(arr) + 1);
        arr[High(arr)] := Party[pIdx].Cards[j];
      end else
        if f then break;
  end;

  // джокер всегда в конце
  f := false;
  for j := 0 to Length(Party[pIdx].Cards) - 1 do
    if GetCardLear(Party[pIdx].Cards[j]) = lnNone then
    begin
      f := true;
      SetLength(arr, Length(arr) + 1);
      arr[High(arr)] := Party[pIdx].Cards[j];
    end else
      if f then break;

  for i := 0 to Length(arr) - 1 do
    Exchange2(arr, Party[pIdx].Cards, i, i);
end;

procedure TCustomGame.CopyStat(RecId: integer; ShowTotal: boolean);
var
  i: integer;

begin
  if not StatTable.Locate('ID', RecId, []) then exit;

  StatTable.DisableControls;
  try
    StatTable.Edit;
    for i := 0 to Length(Party) - 1 do
    begin
      if Party[i].Order > 0 then StatTable.FieldByName('P' + IntToStr(i) + 'ORDER').AsInteger := Party[i].Order
      else if Party[i].Order = 0 then StatTable.FieldByName('P' + IntToStr(i) + 'ORDER').AsString := '-'
      else StatTable.FieldByName('P' + IntToStr(i) + 'ORDER').Clear;

      if Party[i].Take > 0 then StatTable.FieldByName('P' + IntToStr(i) + 'TAKE').AsInteger := Party[i].Take
      else if Party[i].Take = 0 then StatTable.FieldByName('P' + IntToStr(i) + 'TAKE').AsString := '-'
      else StatTable.FieldByName('P' + IntToStr(i) + 'TAKE').Clear;

      if ShowTotal then
        StatTable.FieldByName('P' + IntToStr(i) + 'POINTS').AsInteger := Party[i].Total;
    end;
    StatTable.Post;
  finally
    StatTable.EnableControls;
  end;
end;

function TCustomGame.CountCards(Lear: TLearName; Cards: TCards): integer;
var
  i: integer;

begin
  // кол-во карт указанной масти
  result := 0;
  for i := 0 to Length(Cards) - 1 do
    if (GetCardLear(Cards[i]) = Lear) then Inc(result);
end;

function TCustomGame.CountCards(Lear: TLearName; Cards: TCards; ExCard: TCard): integer;
var
  i: integer;

begin
  // кол-во карт указанной масти, не считая ExCard
  result := 0;
  for i := 0 to Length(Cards) - 1 do
    if (GetCardLear(Cards[i]) = Lear) and (Cards[i] <> ExCard) then Inc(result);
end;

function TCustomGame.StartLearCardOrd(Lear: TLearName): integer;
begin
  case Lear of
    lnHearts: result := 0;
    lnDiamonds: result := 13;
    lnClubs: result := 26;
    lnSpades: result := 39;
  end;

  if Deck = dsz36 then Inc(result, 4);
end;

procedure TCustomGame.StartGame(Interrupted: boolean);
var
  i: integer;
  h: boolean;
  s, pl: string;

begin
  // обнуляем данные игры
  InitializeGameData(false);
  Randomize;

  // статистика пользователей
  h := False;
  try
    for i := 0 to Length(Party) - 1 do
    begin
      if s = '' then s := Player[i].Name
      else s := s + ', ' + Player[i].Name;

      if (Party[i].Index > -1) then
      begin
        Inc(Players[Party[i].Index].cAll);
        if Player[i].Control = ctHumanLocal then
        begin
          h := true;
          pl := Player[i].Name;
          if Interrupted then Inc(Players[Party[i].Index].cInterrupted);
        end;
      end else
        raise Exception.Create('Не выбран ирок №' + IntToStr(i) + '!');
    end;
  except
    on e: Exception do
    begin
      if Pos('Не выбран ирок', e.Message) > 0 then raise Exception.Create(e.Message)
      else raise Exception.Create('Недостаточно игроков для начала игры!');
    end;
  end;

  if not h then raise Exception.Create('Среди игроков партии нет ни одного человека!');

  if KeepLog then
  begin
    if FileExists(DataDir + LOG_FILE) then DeleteFile(DataDir + LOG_FILE);
    AddToLog(DataDir + LOG_FILE, '*****************************************************'#13#10'Начало игры.' +
      #13#10'Игроки: ' + s, 0);
  end;

  if FileExists(DataDir + Format(SAVE_FILE, [pl])) then DeleteFile(DataDir + Format(SAVE_FILE, [pl]));
    
  SavePlayers;
  GameTime := Now;

  // размер колоды
  case Deck of
    dsz36: DeckSz := 36;
    dsz54:
      if NoJoker then DeckSz := 51
      else DeckSz := 54;
  end;

  // проверим параметры раздач
  if (not (goAsc in GameOptions)) and (not (goDesc in GameOptions)) then
    GameOptions := GameOptions + [goAsc, goDesc];
  if (not (goEven in GameOptions)) and (not (goNotEven in GameOptions)) then
    GameOptions := GameOptions + [goEven, goNotEven];
  // заполняем раздачи партии
  FillDeals;
  // раздаем карты - первая раздача
  DealCards;

  FStarted := true;
  // отрисовка раздачи
  if Assigned(FDrawProc) then FDrawProc(false);
  // переходжим к следующему шагу
  Inc(FCurrStep);
  Next;
end;

procedure TCustomGame.StopGame(Normal: boolean);
var
  i: integer;

begin
  if not FStarted then exit;
  GameTime := Now - GameTime;

  if KeepLog then
  begin
    if not Normal then AddToLog(DataDir + LOG_FILE, 'Игра брошена.'#13#10, GameTime);
    AddToLog(DataDir + LOG_FILE, 'Конец игры.'#13#10'-----------------------------------------------------'#13#10, 0);
  end;

  // если игра была брошена, то добавить в статистику игрока, что он бросил игру
  if not Normal then
  begin
    for i := 0 to Length(Party) - 1 do
      if (Party[i].Index > -1) and (Player[i].Control = ctHumanLocal) then
      begin
        Inc(Players[Party[i].Index].cInterrupted);
      end;

    if FileExists(DataDir + Format(SAVE_FILE, [Player[2].Id])) then
      DeleteFile(DataDir + Format(SAVE_FILE, [Player[2].Id]));
  end;

  InitializeGameData(true);
  FStarted := false;
  SavePlayers;
end;

end.
