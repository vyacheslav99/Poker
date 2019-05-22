unit main;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, utils, ExtCtrls, JvBackgrounds, ImgList, settings, ActnList, Menus,
  players, start, selPlayer, ComCtrls, MemTableDataEh, Db, MemTableEh, DBGridEhGrouping, GridsEh,
  DBGridEh, StdCtrls, Spin, engine, engine_net, Math, ShellAPI;

type
  TFMain = class(TForm)
    bgImage: TJvBackground;
    ilBacks: TImageList;
    MainMenu: TMainMenu;
    ActionList: TActionList;
    ilActions: TImageList;
    N1: TMenuItem;
    N2: TMenuItem;
    N3: TMenuItem;
    ASettings: TAction;
    AExit: TAction;
    N4: TMenuItem;
    N5: TMenuItem;
    AEscAction: TAction;
    TrayIcon: TTrayIcon;
    pmTray: TPopupMenu;
    N6: TMenuItem;
    N7: TMenuItem;
    ilDeckRus: TImageList;
    ilDeckSol: TImageList;
    ilDeckSlav: TImageList;
    ilDeckSouv: TImageList;
    ilDeckEng: TImageList;
    ilLear: TImageList;
    APlayers: TAction;
    N8: TMenuItem;
    N9: TMenuItem;
    AStartGame: TAction;
    N10: TMenuItem;
    AStopGame: TAction;
    N11: TMenuItem;
    AHoldGame: TAction;
    AEscAction1: TMenuItem;
    N12: TMenuItem;
    StatusBar: TStatusBar;
    tmrStart: TTimer;
    mtGameStat: TMemTableEh;
    mtGameStatP0POINTS: TIntegerField;
    mtGameStatP1POINTS: TIntegerField;
    dsoGameStat: TDataSource;
    mtGameStatDEAL_NAME: TStringField;
    dbgGameData: TDBGridEh;
    bvTable: TBevel;
    lbPlayer1: TLabel;
    lbPlayer2: TLabel;
    lbPlayer3: TLabel;
    lbBet: TLabel;
    btnNextAction: TButton;
    pFace1: TPanel;
    imFace1: TImage;
    pFace2: TPanel;
    imFace2: TImage;
    pFace3: TPanel;
    imFace3: TImage;
    pTrump: TPanel;
    imTrump: TImage;
    pTblCard1: TPanel;
    imTblCard1: TImage;
    pTblCard2: TPanel;
    imTblCard2: TImage;
    pTblCard3: TPanel;
    imTblCard3: TImage;
    mtGameStatID: TIntegerField;
    mtGameStatDEAL_NO: TIntegerField;
    mtGameStatP2POINTS: TIntegerField;
    mtGameStatP0ORDER: TStringField;
    mtGameStatP0TAKE: TStringField;
    mtGameStatP1ORDER: TStringField;
    mtGameStatP1TAKE: TStringField;
    mtGameStatP2ORDER: TStringField;
    mtGameStatP2TAKE: TStringField;
    lbInfo: TLabel;
    lbPlayer1Order: TLabel;
    lbPlayer2Order: TLabel;
    lbDeal: TLabel;
    lbPlayer3Order: TLabel;
    lbPlayer1Take: TLabel;
    lbPlayer2Take: TLabel;
    lbPlayer3Take: TLabel;
    btnSkipDeal: TButton;
    tmrGameTime: TTimer;
    AShowAgreements: TAction;
    N13: TMenuItem;
    cbBet: TComboBox;
    AOpenLog: TAction;
    N14: TMenuItem;
    mProfile: TMenuItem;
    lbTableCard1: TLabel;
    lbTableCard2: TLabel;
    lbTableCard3: TLabel;
    ADebugMode: TAction;
    APicConfig: TAction;
    N15: TMenuItem;
    AGameGraph: TAction;
    N16: TMenuItem;
    procedure FormCreate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormShow(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure ASettingsExecute(Sender: TObject);
    procedure AExitExecute(Sender: TObject);
    procedure AEscActionExecute(Sender: TObject);
    procedure FormHide(Sender: TObject);
    procedure TrayIconClick(Sender: TObject);
    procedure APlayersExecute(Sender: TObject);
    procedure AStartGameUpdate(Sender: TObject);
    procedure AStartGameExecute(Sender: TObject);
    procedure AStopGameExecute(Sender: TObject);
    procedure AStopGameUpdate(Sender: TObject);
    procedure tmrStartTimer(Sender: TObject);
    procedure FormResize(Sender: TObject);
    procedure btnNextActionClick(Sender: TObject);
    procedure btnSkipDealClick(Sender: TObject);
    procedure tmrGameTimeTimer(Sender: TObject);
    procedure AShowAgreementsExecute(Sender: TObject);
    procedure cbBetKeyDown(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure AOpenLogExecute(Sender: TObject);
    procedure AOpenLogUpdate(Sender: TObject);
    procedure imFace1DblClick(Sender: TObject);
    procedure ADebugModeExecute(Sender: TObject);
    procedure APicConfigExecute(Sender: TObject);
    procedure AGameGraphExecute(Sender: TObject);
  private
    NoStart, NoStart2: boolean;
    Game: TGame;
    CardsObiects: array of TCardsObj;
    FDbgMode: boolean;
    procedure InitializeGame(AGameType: TGameType);
    procedure OnAppException(Sender: TObject; E: Exception);
    procedure OnPlayerCardClick(Sender: TObject);
    procedure StartGame;
    procedure StopGame(AHold: boolean);
    procedure SaveWndState;
    procedure ApplySettings;
    procedure DistributeObjects;
    procedure ShowGameControls(AShow: boolean);
    procedure FreeGameObjects;
    procedure FreeCards;
    procedure DrawObjects(Full: boolean);
    procedure RefreshCards;
    procedure SetPlayerConsole(SetType: integer);
    procedure SetMessage(Target: TMsgLabel; Text: string; Delay: integer; CanClearAll: boolean; ShowMsgBox: boolean);
    procedure NextStep;
    procedure CreateProfilesMenu;
    procedure OnProfileMenuItem(Sender: TObject);
    procedure ShowPlayerInfo(pIdx: integer);
    procedure SetDbgMode(const Value: boolean);
    function ShowGameMsg(ACaption, AMessage: string; Flags: integer = 0): boolean;
    procedure LoadToImageList(ResFolder: string; il: TImageList);
  public
    property DbgMode: boolean read FDbgMode write SetDbgMode; 
  end;

var
  FMain: TFMain;

implementation

uses robotParams, humanParams, wjoker, msg_box, selimage, gchart;

{$R *.dfm}

{ TFMain }

procedure TFMain.ADebugModeExecute(Sender: TObject);
var
  b: boolean;

begin
  b := FSettings.FirstDbgMode;
  DbgMode := not DbgMode;

  if DbgMode and b then
    Application.MessageBox(pchar('Включен режим отладки! Включено ведение лога игры. Запись лога НЕ выключается автоматически ' +
      'при отключении режима отладки. Если нужно выключить, то это можно сделать вручную в настройках.'), 'Внимание',
      MB_OK + MB_ICONWARNING);
end;

procedure TFMain.AEscActionExecute(Sender: TObject);
var
  Ico: TIcon;

begin
  if FSettings.EscAction <> eaNone then
  begin
    if FSettings.EscSetCaption <> '' then
    begin
      Application.Title := FSettings.EscSetCaption;
      Caption := FSettings.EscSetCaption;
      TrayIcon.Hint := FSettings.EscSetCaption;
    end;

    if FileExists(FSettings.EscSetIcon) then
    begin
      if LowerCase(ExtractFileExt(FSettings.EscSetIcon)) = '.exe' then
      begin
        try
          Ico := TIcon.Create;
          GetFileIcon(FSettings.EscSetIcon, Ico);
          Application.Icon.Assign(Ico);
          Icon.Assign(Ico);
          TrayIcon.Icon.Assign(Ico);
        finally
          Ico.Free;
        end;
      end else
      begin
        Application.Icon.LoadFromFile(FSettings.EscSetIcon);
        Icon.LoadFromFile(FSettings.EscSetIcon);
        TrayIcon.Icon.LoadFromFile(FSettings.EscSetIcon);
      end;
    end;
  end;

  case FSettings.EscAction of
    eaNone, eaChangeCaption: exit;
    eaMinimize: WindowState := wsMinimized;
    eaHideOnTray:
    begin
      TrayIcon.Visible := true;
      Hide;
    end;
    eaClose: Close;
  end;
end;

procedure TFMain.AExitExecute(Sender: TObject);
begin
  Close;
end;

procedure TFMain.AGameGraphExecute(Sender: TObject);
var
  FGameChart: TFGameChart;

begin
  FGameChart := TFGameChart.Create(self);
  try
    FGameChart.DBChart.Series[0].Title := Game.Player[0].Name;
    FGameChart.DBChart.Series[1].Title := Game.Player[1].Name;
    FGameChart.DBChart.Series[2].Title := Game.Player[2].Name;
    FGameChart.ShowModal;
  finally
    FGameChart.Free;
  end;
end;

procedure TFMain.AOpenLogExecute(Sender: TObject);
begin
  if FileExists(FSettings.DataDir + LOG_FILE) then
    ShellExecute(Handle, 'open', pchar(FSettings.DataDir + LOG_FILE), '', pchar(FSettings.DataDir), SW_SHOWNORMAL);
end;

procedure TFMain.AOpenLogUpdate(Sender: TObject);
begin
  TAction(Sender).Enabled := FileExists(FSettings.DataDir + LOG_FILE);
end;

procedure TFMain.APicConfigExecute(Sender: TObject);
var
  FPic: TFSelImage;

begin
  FPic := TFSelImage.Create(self);
  try
    FPic.btnSave.Visible := false;
    FPic.btnCancel.Caption := 'Закрыть';
    FPic.ShowModal;
  finally
    FPic.Free;
  end;
end;

procedure TFMain.APlayersExecute(Sender: TObject);
var
  pf: TFPlayers;

begin
  pf := TFPlayers.Create(self);
  try
    //pf.btnResetAllStat.Visible := DbgMode;
    pf.Players := Game.Players;
    if pf.ShowModal = mrOk then
    begin
      Game.Players := pf.Players;
      Game.SavePlayers;
    end;
  finally
    pf.Free;
  end;
end;

procedure TFMain.ApplySettings;
var
  i: integer;
  rfn: string;

begin
  CreateProfilesMenu;
  StatusBar.Panels[1].Text := FSettings.cbProfile.Items.Strings[FSettings.Profile];
  Color := FSettings.TableBgColor;
  if FSettings.TableBg > 0 then
  begin
    rfn := FSettings.DataDir + BG_DIR + FSettings.TableBgFile;

    if FileExists(rfn) then
      bgImage.Image.Picture.LoadFromFile(rfn)
    else
      Application.MessageBox(pchar('Не удалось загрузить фоновый рисунок! Файл "' + BG_DIR + FSettings.TableBgFile + '" не существует.'),
        'Ошибка', MB_OK + MB_ICONERROR);

    //bgImage.Image.Picture.Bitmap.LoadFromResourceName(HInstance, 'BG' + IntToStr(FSettings.TableBg));
  end else
    bgImage.Image.Picture.Bitmap.Assign(nil);

  lbPlayer1.Font.Assign(FSettings.ScrFont);
  lbPlayer1Order.Font.Assign(FSettings.ScrFont);
  lbPlayer1Take.Font.Assign(FSettings.ScrFont);
  lbPlayer2.Font.Assign(FSettings.ScrFont);
  lbPlayer2Order.Font.Assign(FSettings.ScrFont);
  lbPlayer2Take.Font.Assign(FSettings.ScrFont);
  lbPlayer3.Font.Assign(FSettings.ScrFont);
  lbPlayer3Order.Font.Assign(FSettings.ScrFont);
  lbPlayer3Take.Font.Assign(FSettings.ScrFont);
  lbBet.Font.Assign(FSettings.ScrFont);
  lbInfo.Font.Assign(FSettings.ScrFont);
  lbDeal.Font.Assign(FSettings.ScrFont);
  lbTableCard1.Font.Assign(FSettings.ScrFont);
  lbTableCard2.Font.Assign(FSettings.ScrFont);
  lbTableCard3.Font.Assign(FSettings.ScrFont);
  Game.WaitDelay := FSettings.WaitDelay;
  Game.SortDirect := FSettings.SortDirection;
  Game.LearOrder := FSettings.GetLearOrder;
  Game.KeepLog := FSettings.KeepLog;
  Game.SaveEachStep := FSettings.SaveEachStep;
  AOpenLog.Visible := FSettings.KeepLog;

  dbgGameData.FixedColor := FSettings.GridTitleBgColor;
  dbgGameData.Color := FSettings.GridBgColor;
  dbgGameData.EvenRowColor := FSettings.GridBgColor;
  dbgGameData.TitleFont.Color := FSettings.GridTitleFontColor;
  dbgGameData.Font.Color := FSettings.GridFontColor;
  for i := 0 to dbgGameData.Columns.Count - 1 do
  begin
    //dbgGameData.Columns[i].Title.Font.Color := FSettings.GridTitleFontColor;
    dbgGameData.Columns[i].Font.Color := FSettings.GridFontColor;
    if dbgGameData.Columns[i].FieldName = 'DEAL_NAME' then
    begin
      dbgGameData.Columns[i].Color := FSettings.GridBgDealColor;
      dbgGameData.Columns[i].Font.Color := FSettings.GridFontDealColor;
    end else
    if (dbgGameData.Columns[i].FieldName = 'P0TAKE') or (dbgGameData.Columns[i].FieldName = 'P1TAKE') or
      (dbgGameData.Columns[i].FieldName = 'P2TAKE') then
    begin
      dbgGameData.Columns[i].Color := FSettings.GridBgTakeColor;
      dbgGameData.Columns[i].Font.Color := FSettings.GridFontTakeColor;
    end else
    if (dbgGameData.Columns[i].FieldName = 'P0POINTS') or (dbgGameData.Columns[i].FieldName = 'P1POINTS') or
      (dbgGameData.Columns[i].FieldName = 'P2POINTS') then
    begin
      dbgGameData.Columns[i].Color := FSettings.GridBgScoresColor;
      dbgGameData.Columns[i].Font.Color := FSettings.GridFontScoresColor;
    end;
  end;

  DrawObjects(false);
end;

procedure TFMain.ASettingsExecute(Sender: TObject);
begin
  if FSettings.ShowModal = mrOk then ApplySettings;
end;

procedure TFMain.AShowAgreementsExecute(Sender: TObject);
begin
  FStartDialog.Execute('', Game, true);
end;

procedure TFMain.AStartGameExecute(Sender: TObject);
begin
  if NoStart2 then exit;
  NoStart2 := true;
  StartGame;
  NoStart2 := false;
end;

procedure TFMain.AStartGameUpdate(Sender: TObject);
begin
  TAction(Sender).Enabled := not Game.Started;
end;

procedure TFMain.AStopGameExecute(Sender: TObject);
begin
  StopGame(TAction(Sender) = AHoldGame);
end;

procedure TFMain.AStopGameUpdate(Sender: TObject);
begin
  TAction(Sender).Enabled := Game.Started;
end;

procedure TFMain.btnNextActionClick(Sender: TObject);
begin
  NextStep;
end;

procedure TFMain.btnSkipDealClick(Sender: TObject);
begin
  if (Application.MessageBox('Пропустить раздачу?', 'Подтверждение', MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;    
  Game.SkipDeal;
end;

procedure TFMain.cbBetKeyDown(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  case Key of
    VK_RETURN: NextStep;
    Ord('0'), VK_NUMPAD0, Ord('G'), Ord('g'), VK_SPACE, Ord('-'), VK_OEM_MINUS: cbBet.ItemIndex := 0;
  end;
end;

procedure TFMain.CreateProfilesMenu;
var
  m: TMenuItem;
  i: integer;

begin
  mProfile.Clear;
  for i := 0 to FSettings.cbProfile.Items.Count - 1 do
  begin
    try
      m := TMenuItem.Create(self);
      m.Caption := FSettings.cbProfile.Items.Strings[i];
      m.Hint := 'Загрузить профиль ' + FSettings.cbProfile.Items.Strings[i];
      m.Tag := i;
      m.Visible := true;
      m.OnClick := OnProfileMenuItem;
      m.RadioItem := true;
      m.Checked := FSettings.Profile = i;
      mProfile.Add(m);
    except
      m.Free;
    end;
  end;
end;

procedure TFMain.DistributeObjects;
var
  i, j, l: integer;
  ind, x{, learSp}: integer;
  aw, rw: integer;
  oldLear: TLearName;
  
begin
  // изображения и имена игроков
  pFace1.Left := 10;
  pFace1.Top := 10;
  lbPlayer1.Left := 10;
  lbPlayer1.Top := pFace1.Top + pFace1.Height + 5;
  lbPlayer1Order.Left := 10;
  lbPlayer1Order.Top := lbPlayer1.Top + lbPlayer1.Height + 3;
  lbPlayer1Take.Left := 10;
  lbPlayer1Take.Top := lbPlayer1Order.Top + lbPlayer1Order.Height;
  pFace2.Left := ClientWidth - pFace2.Width - 10;
  pFace2.Top := 10;
  lbPlayer2.Left := ClientWidth - lbPlayer2.Width - 10;
  lbPlayer2.Top := pFace2.Top + pFace2.Height + 5;
  lbPlayer2Order.Left := ClientWidth - lbPlayer2Order.Width - 10;
  lbPlayer2Order.Top := lbPlayer2.Top + lbPlayer2.Height + 3;
  lbPlayer2Take.Left := ClientWidth - lbPlayer2Take.Width - 10;
  lbPlayer2Take.Top := lbPlayer2Order.Top + lbPlayer2Order.Height;
  // таблица игры
  dbgGameData.Left := ClientWidth - dbgGameData.Width - 10;
  dbgGameData.Top := lbPlayer2Take.Top + lbPlayer2Take.Height + 10;
  dbgGameData.Height := ClientHeight - dbgGameData.Top - StatusBar.Height - 10;
  //
  pFace3.Left := 10;
  pFace3.Top := ClientHeight - Round(pFace3.Height * 2) - StatusBar.Height - 15;
  lbPlayer3.Left := 10;
  lbPlayer3.Top := pFace3.Top + pFace3.Height + 2;
  lbPlayer3Order.Left := 10;
  lbPlayer3Order.Top := lbPlayer3.Top + lbPlayer3.Height + 3;
  lbPlayer3Take.Left := 10;
  lbPlayer3Take.Top := lbPlayer3Order.Top + lbPlayer3Order.Height;
  // игровой стол
  bvTable.Left := Round(ClientWidth / 4);
  bvTable.Top := Round(ClientHeight / 3);
  pTblCard1.Left := bvTable.Left + 15;
  pTblCard2.Left := pTblCard1.Left + pTblCard1.Width + 25;
  pTblCard3.Left := pTblCard2.Left + pTblCard2.Width + 25;
  pTblCard1.Top := bvTable.Top + 35;
  pTblCard2.Top := bvTable.Top + 35 {+ Round(pTblCard2.Height / 2)};
  pTblCard3.Top := bvTable.Top + 35;
  lbTableCard1.Left := pTblCard1.Left;
  lbTableCard2.Left := pTblCard2.Left;
  lbTableCard3.Left := pTblCard3.Left;
  lbTableCard1.Top := bvTable.Top + 8;
  lbTableCard2.Top := bvTable.Top + 8;
  lbTableCard3.Top := bvTable.Top + 8;
  //pTrump.Left := bvTable.Left + bvTable.Width + 6;
  pTrump.Left := bvTable.Left - pTrump.Width - 10;
  pTrump.Top := bvTable.Top + Round(bvTable.Height * 0.33);
  lbInfo.Top := bvTable.Top - 20;
  lbInfo.Left := Round(ClientWidth / 2.5) - Round(lbInfo.Width / 2); // bvTable.Left;
  lbDeal.Top := bvTable.Top - 40;
  lbDeal.Left := Round(ClientWidth / 2.5) - Round(lbDeal.Width / 2); // bvTable.Left;
  // эл-ты управления пользователя
  lbBet.Left := bvTable.Left;
  lbBet.Top := bvTable.Top + bvTable.Height + 15;
  cbBet.Left := lbBet.Left;
  cbBet.Top := lbBet.Top + lbBet.Height + 3;
  btnNextAction.Left := cbBet.Left;
  btnNextAction.Top := cbBet.Top + cbBet.Height + 6;
  btnSkipDeal.Left := btnNextAction.Left + btnNextAction.Width + 6;
  btnSkipDeal.Top := btnNextAction.Top;

  // карты игроков
  x := 3;
  //learSp := 5;
  for i := 0 to Length(CardsObiects) - 1 do
  begin
    case i of
      0:
      begin
        // игрок 1 (слева вверху)
        ind := 3;
        l := Length(CardsObiects[i]);
        rw := (l * (71 + ind + x));
        aw := (Round(ClientWidth / 2) - (pFace1.Left + pFace1.Width + 10)) - 30;
        while rw >= aw do
        begin
          Inc(ind, -1);
          rw := (l * (71 + ind + x));
        end;
        for j := 0 to Length(CardsObiects[i]) - 1 do
        begin
          CardsObiects[i][j].Top := pFace1.Top;
          if j = 0 then CardsObiects[i][j].Left := pFace1.Left + pFace1.Width + 10
          else CardsObiects[i][j].Left := CardsObiects[i][j-1].Left + CardsObiects[i][j-1].Width + ind;
        end;
      end;
      1:
      begin
        // игрок 2 (право верх)
        ind := 3;
        l := Length(CardsObiects[i]);
        rw := (l * (71 + ind + x));
        aw := (Round(ClientWidth / 2) - (pFace2.Width + 10)) - 30;
        while rw >= aw do
        begin
          Inc(ind, -1);
          rw := (l * (71 + ind + x));
        end;
        for j := 0 to Length(CardsObiects[i]) - 1 do
        begin
          CardsObiects[i][j].Top := pFace2.Top;
          if j = 0 then CardsObiects[i][j].Left := pFace2.Left - CardsObiects[i][j].Width - 10
          else CardsObiects[i][j].Left := pFace2.Left - CardsObiects[i][j].Width - 10 - ((CardsObiects[i][j].Width + ind) * j);
        end;
      end;
      2:
      begin
        // игрок 3 - пользователь (низ)
        ind := 3;
        l := Length(CardsObiects[i]);
        rw := (l * (71 + ind + x));
        aw := (ClientWidth - (pFace3.Left + pFace3.Width + 10) - (dbgGameData.Width + 10));
        {if FSettings.SeparateLear then
        begin
          rw := rw + (learSp * 5);
          aw := aw - 100;
        end;}
        while rw >= aw do
        begin
          Inc(ind, -1);
          rw := (l * (71 + ind + x));
          //if FSettings.SeparateLear then rw := rw + (learSp * 5);
        end;
        for j := 0 to Length(CardsObiects[i]) - 1 do
        begin
          CardsObiects[i][j].Top := ClientHeight - CardsObiects[i][j].Height - StatusBar.Height - 10;
          if j = 0 then
          begin
            CardsObiects[i][j].Left := Round(aw / 2) - Round(rw / 2);
            if CardsObiects[i][j].Left < pFace3.Left + pFace3.Width + 10 then
              CardsObiects[i][j].Left := pFace3.Left + pFace3.Width + 10;
            //oldLear := Game.GetCardLear(Game.Party[2].Cards[CardsObiects[i][j].Tag]);
          end else
          begin
            {if FSettings.SeparateLear and
              (Game.GetCardLear(Game.Party[2].Cards[CardsObiects[i][j].Tag]) <> oldLear) and
              ((Game.CurrDeal.Deal <> dDark) or ((Game.CurrDeal.Deal = dDark) and (not Game.IsBet))) then
            begin
              CardsObiects[i][j].Left := CardsObiects[i][j-1].Left + CardsObiects[i][j-1].Width + learSp;
              oldLear := Game.GetCardLear(Game.Party[2].Cards[CardsObiects[i][j].Tag]);
            end else}
              CardsObiects[i][j].Left := CardsObiects[i][j-1].Left + CardsObiects[i][j-1].Width + ind;
          end;
        end;
      end;
    end;
  end;
  Application.ProcessMessages;
end;

procedure TFMain.DrawObjects(Full: boolean);
begin
  if Full then
  begin
    // первая отрисовка всех объектов партии
    lbInfo.Caption := '';
    lbDeal.Caption := '';
    lbTableCard1.Caption := '';
    lbTableCard2.Caption := '';
    lbTableCard3.Caption := '';
    lbPlayer1.Caption := Game.Player[0].Name;
    lbPlayer1Order.Caption := '';
    lbPlayer1Take.Caption := '';
    imFace1.Hint := Game.Player[0].Name + #13#10 + DifficultyAsString(Game.Player[0].Difficulty);
    pFace1.Hint := Game.Player[0].Name + #13#10 + DifficultyAsString(Game.Player[0].Difficulty);
    if FileExists(FSettings.DataDir + USER_DATA_DIR + Game.Player[0].FaceFile) then
      imFace1.Picture.LoadFromFile(FSettings.DataDir + USER_DATA_DIR + Game.Player[0].FaceFile)
    else
      imFace1.Picture.Assign(nil);

    lbPlayer2.Caption := Game.Player[1].Name;
    lbPlayer2Order.Caption := '';
    lbPlayer2Take.Caption := '';
    imFace2.Hint := Game.Player[1].Name + #13#10 + DifficultyAsString(Game.Player[1].Difficulty);
    pFace2.Hint := Game.Player[1].Name + #13#10 + DifficultyAsString(Game.Player[1].Difficulty);
    if FileExists(FSettings.DataDir + USER_DATA_DIR + Game.Player[1].FaceFile) then
      imFace2.Picture.LoadFromFile(FSettings.DataDir + USER_DATA_DIR + Game.Player[1].FaceFile)
    else
      imFace2.Picture.Assign(nil);

    lbPlayer3.Caption := Game.Player[2].Name;
    lbPlayer3Order.Caption := '';
    lbPlayer3Take.Caption := '';
    imFace3.Hint := Game.Player[2].Name;
    pFace3.Hint := Game.Player[2].Name;
    if FileExists(FSettings.DataDir + USER_DATA_DIR + Game.Player[2].FaceFile) then
      imFace3.Picture.LoadFromFile(FSettings.DataDir + USER_DATA_DIR + Game.Player[2].FaceFile)
    else
      imFace3.Picture.Assign(nil);

    imTrump.Picture.Assign(nil);
    imTrump.Hint := '';
    
    ShowGameControls(true);
  end;

  RefreshCards;
  DistributeObjects;
  Application.ProcessMessages;
end;

procedure TFMain.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  SaveWndState;
  if Game.Started then Game.HoldGame;
end;

procedure TFMain.FormCreate(Sender: TObject);
{var
  e: string;}

begin
  Application.OnException := OnAppException;

  // рубашки
  LoadToImageList(ExtractFilePath(Application.ExeName) + DATA_DIR + BACK_DIR, ilBacks);
  // русская
  LoadToImageList(ExtractFilePath(Application.ExeName) + DATA_DIR + DECK_RUS_DIR, ilDeckRus);
  // пасьянсовая
  LoadToImageList(ExtractFilePath(Application.ExeName) + DATA_DIR + DECK_SOL_DIR, ilDeckSol);
  // славянская
  LoadToImageList(ExtractFilePath(Application.ExeName) + DATA_DIR + DECK_SLAV_DIR, ilDeckSlav);
  // сувенирная
  LoadToImageList(ExtractFilePath(Application.ExeName) + DATA_DIR + DECK_SOUV_DIR, ilDeckSouv);
  // буржуйская
  LoadToImageList(ExtractFilePath(Application.ExeName) + DATA_DIR + DECK_ENG_DIR, ilDeckEng);

  FDbgMode := false;
  NoStart := false;
  NoStart2 := false;
  FSettings := TFSettings.Create(self);
  InitializeGame(gtLocal);
  FStartDialog := TFStartDialog.Create(self);
  ShowGameControls(false);
end;

procedure TFMain.FormDestroy(Sender: TObject);
begin
  FStartDialog.Free;
  Game.Free;
  FSettings.Free;
  FreeGameObjects;
end;

procedure TFMain.FormHide(Sender: TObject);
begin
  SaveWndState;
end;

procedure TFMain.FormResize(Sender: TObject);
begin
  DistributeObjects;
end;

procedure TFMain.FormShow(Sender: TObject);
begin
  Top := FSettings.WTop;
  Left := FSettings.WLeft;
  Width := FSettings.WWidth;
  Height := FSettings.WHeight;
  if FSettings.WMaximized then WindowState := wsMaximized
  else WindowState := wsNormal;

  TrayIcon.Hint := Application.Title;
  TrayIcon.Icon := Application.Icon;
  TrayIcon.Visible := false;
  ApplySettings;
  if (not NoStart) and FSettings.AutoStart then tmrStart.Enabled := true;
  NoStart := true;
end;

procedure TFMain.FreeCards;
var
  i, j: integer;

begin
  for i := 0 to Length(CardsObiects) - 1 do
  begin
    for j := 0 to Length(CardsObiects[i]) - 1 do
      if (CardsObiects[i][j] <> nil) and Assigned(CardsObiects[i][j]) then FreeAndNil(CardsObiects[i][j]);

    SetLength(CardsObiects[i], 0);
  end;
  SetLength(CardsObiects, 0);
end;

procedure TFMain.FreeGameObjects;
begin
  FreeCards;
end;

procedure TFMain.imFace1DblClick(Sender: TObject);
var
  i: integer;

begin
  if (Sender = imFace1) or (Sender = pFace1) then i := 0
  else if (Sender = imFace2) or (Sender = pFace2) then i := 1
  else if (Sender = imFace3) or (Sender = pFace3) then i := 2
  else exit;

  ShowPlayerInfo(i);
end;

procedure TFMain.InitializeGame(AGameType: TGameType);
begin
  if Assigned(Game) then FreeAndNil(Game);
  case AGameType of
    gtLocal: Game := TGame.Create(mtGameStat, DrawObjects, SetPlayerConsole, SetMessage);
    gtServer: Game := TGameServer.Create(mtGameStat, DrawObjects, SetPlayerConsole, SetMessage);
    gtClient: Game := TGameClient.Create(mtGameStat, DrawObjects, SetPlayerConsole, SetMessage);
  end;
  Game.GameType := AGameType;
  Game.DataDir := FSettings.DataDir;
  Game.LoadPlayers;
  Game.WaitDelay := FSettings.WaitDelay;
  Game.SortDirect := FSettings.SortDirection;
  Game.LearOrder := FSettings.GetLearOrder;
  Game.KeepLog := FSettings.KeepLog;
  Game.SaveEachStep := FSettings.SaveEachStep;
  Game.SynchGameParams := FStartDialog.DoSynchGameParams;
end;

procedure TFMain.LoadToImageList(ResFolder: string; il: TImageList);

  function _getImgName(idx: integer): string;
  begin
    case idx of
      0: result := '2ч';
      1: result := '3ч';
      2: result := '4ч';
      3: result := '5ч';
      4: result := '6ч';
      5: result := '7ч';
      6: result := '8ч';
      7: result := '9ч';
      8: result := '10ч';
      9: result := 'Вч';
      10: result := 'Дч';
      11: result := 'Кч';
      12: result := 'Тч';

      13: result := '2б';
      14: result := '3б';
      15: result := '4б';
      16: result := '5б';
      17: result := '6б';
      18: result := '7б';
      19: result := '8б';
      20: result := '9б';
      21: result := '10б';
      22: result := 'Вб';
      23: result := 'Дб';
      24: result := 'Кб';
      25: result := 'Тб';

      26: result := '2к';
      27: result := '3к';
      28: result := '4к';
      29: result := '5к';
      30: result := '6к';
      31: result := '7к';
      32: result := '8к';
      33: result := '9к';
      34: result := '10к';
      35: result := 'Вк';
      36: result := 'Дк';
      37: result := 'Кк';
      38: result := 'Тк';

      39: result := '2п';
      40: result := '3п';
      41: result := '4п';
      42: result := '5п';
      43: result := '6п';
      44: result := '7п';
      45: result := '8п';
      46: result := '9п';
      47: result := '10п';
      48: result := 'Вп';
      49: result := 'Дп';
      50: result := 'Кп';
      51: result := 'Тп';

      52: result := 'дж2';
      53: result := 'дж1';
    end;
    result := result + '.bmp';
  end;

var
  i: integer;
  b: TBitmap;

begin
  b := TBitmap.Create;

  try
    il.Clear;
    if il = ilBacks then
    begin
      for i := 1 to CountFiles(ResFolder) do
      begin
        b.LoadFromFile(ResFolder + '\back' + IntToStr(i) + '.bmp');
        il.AddMasked(b, RGB(255, 85, 255));
      end;
    end else
    begin
      for i := 0 to 53 do
      begin
        b.LoadFromFile(ResFolder + '\' + _getImgName(i));
        il.AddMasked(b, RGB(255, 85, 255));
      end;
    end;
  finally
    b.Free;
  end;
end;

procedure TFMain.NextStep;
var
  err: string;

begin
  if Game.CanStopGame then
  begin
    Game.StopGame(true);
    ShowGameControls(false);
    FreeGameObjects;
    tmrGameTime.Enabled := false;
    StatusBar.Panels[0].Text := '';
    exit;
  end;
  
  if Game.IsBet then
  begin
    if not Game.MakeOrder(2, cbBet.ItemIndex, err) then
    begin
      SetMessage(lInfo, err, 0, false, true);
      cbBet.SetFocus;
      exit;
    end else
      SetPlayerConsole(-1);
  end else
  begin
    SetPlayerConsole(-1);
  end;
  if Game.CanPause then Game.GiveWalk(not Game.NoWalk);
  Game.Next;
end;

procedure TFMain.OnAppException(Sender: TObject; E: Exception);
begin
  if E is EAccessViolation then
  begin
   // Application.MessageBox(pchar(e.Message), 'Error', MB_OK + MB_ICONERROR);
  end;
end;

procedure TFMain.OnPlayerCardClick(Sender: TObject);
var
  r: boolean;
  err: string;
  ja: TJokerAction;
  jc: TCard;
  wj: TFWalkJoker;
  i, x: integer;
  l: TLearName;

begin
  if Game.IsBet then exit;
  if Game.NoWalk then exit;

  if Game.Party[2].Cards[TImage(Sender).Tag] in [cJoker1, cJoker2] then
  begin
    wj := TFWalkJoker.Create(self);
    try
      wj.cbJokerAction.Items.Add('Забрать');
      wj.cbJokerAction.Items.Add('Выдать за карту');
      if Game.CurrStep = 0 then
      begin
        if Game.JokerMajorLear then wj.cbJokerAction.Items.Add('Забрать по СТАРШЕЙ карте масти');
        if Game.JokerMinorLear then wj.cbJokerAction.Items.Add('Забрать по МЛАДШЕЙ карте масти');
      end else
        wj.cbJokerAction.Items.Add('Скинуть');

      for i := 0 to Ord(lnSpades) do
        if TLearName(i) = Game.Trump then
          wj.cbLear.Items.Add(Game.LearToStr(TLearName(i), '') + ' (козырь)')
        else
          wj.cbLear.Items.Add(Game.LearToStr(TLearName(i), ''));

      if Game.Deck = dsz36 then x := 4
      else x := 0;

      for i := x to 12 do wj.cbCard.Items.Add(Game.CardToStr(TCard(i), false));
      wj.cbCard.DropDownCount := wj.cbCard.Items.Count + 1;

      if wj.ShowModal = mrOk then
      begin
        case wj.cbJokerAction.ItemIndex of
          0:
          begin
            ja := jaCard;
            if (Game.CurrStep = 0) then
            begin
              if (Game.Trump <> lnNone) then jc := Game.ChangeCardLear(chAce, Game.Trump)
              else begin
                l := TLearName(RandomRange(Ord(lnHearts), Ord(lnNone)));
                jc := Game.ChangeCardLear(chAce, l);
              end;
            end else
              if (Game.Trump = lnNone) or Game.StrongJoker then jc := Game.ChangeCardLearToTable(chAce)
              else jc := Game.ChangeCardLear(chAce, Game.Trump);
          end;
          1:
          begin
            ja := jaCard;
            jc := Game.ChangeCardLear(TCard(wj.cbCard.ItemIndex + x), TLearName(wj.cbLear.ItemIndex));
          end;
          2:
          begin
            if wj.cbJokerAction.Text = 'Скинуть' then
            begin
              ja := jaCard;
              {if Game.Deck = dsz36 then jc := Game.ChangeCardLearNoTable(ch6)
              else jc := Game.ChangeCardLearNoTable(ch2);}
              if Game.Deck = dsz36 then jc := Game.ChangeCardLearToTable(ch6)
              else jc := Game.ChangeCardLearToTable(ch2);
            end else
            begin
              ja := jaByMax;
              jc := Game.ChangeCardLear(chAce, TLearName(wj.cbLear.ItemIndex));
            end;
          end;
          3:
          begin
            ja := jaByMin;
            jc := Game.ChangeCardLear(chAce, TLearName(wj.cbLear.ItemIndex));
          end;
          else begin
            Application.MessageBox('Не выбрано действие Джокера', 'Сообщение', MB_OK + MB_ICONERROR);
            exit;
          end;
        end;
      end else exit;
    finally
      wj.Free;
    end;
  end;

  if Game.CurrStep = 0 then r := Game.DoWalk(2, TImage(Sender).Tag, ja, jc, err)
  else r := Game.DoBeat(2, TImage(Sender).Tag, ja, jc, err);
  if r then
  begin
    DrawObjects(false);
    NextStep;
  end else SetMessage(lInfo, err, 0, false, true);
end;

procedure TFMain.OnProfileMenuItem(Sender: TObject);
begin
  FSettings.cbProfile.ItemIndex := TMenuItem(Sender).Tag;
  FSettings.SetProfile(FSettings.cbProfile.ItemIndex);
  ApplySettings;
end;

procedure TFMain.RefreshCards;
var
  i, j: integer;
  im: TImage;
  lb: TLabel;

begin
  FreeCards;
  SetLength(CardsObiects, Length(Game.Party));
  for i := 0 to Length(Game.Party) - 1 do
  begin
    SetLength(CardsObiects[i], Length(Game.Party[i].Cards));
    for j := 0 to Length(Game.Party[i].Cards) - 1 do
    begin
      CardsObiects[i][j] := TImage.Create(nil);
      CardsObiects[i][j].Parent := Self;
      CardsObiects[i][j].AutoSize := false;
      CardsObiects[i][j].Center := true;
      CardsObiects[i][j].Enabled := true;
      CardsObiects[i][j].Height := 96;
      CardsObiects[i][j].Width := 71;
      CardsObiects[i][j].Left := -100;
      CardsObiects[i][j].Top := -100;
      CardsObiects[i][j].Proportional := true;
      CardsObiects[i][j].Stretch := true;
      CardsObiects[i][j].Visible := true;
      if i = 1 then CardsObiects[i][j].SendToBack;
      if Game.Player[i].Control <> ctHumanLocal then
      begin
        if (Game.CurrDeal.Deal = dBrow) or DbgMode then
        begin
          CardsObiects[i][j].ShowHint := true;
          CardsObiects[i][j].Hint := Game.CardToStr(Game.Party[i].Cards[j]);
          case FSettings.DeckType of
            dtRussian: ilDeckRus.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
            dtSolitaire: ilDeckSol.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
            dtSlav: ilDeckSlav.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
            dtSouvenir: ilDeckSouv.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
            dtEnglish: ilDeckEng.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
          end;
        end else ilBacks.GetBitmap(FSettings.CardBack, CardsObiects[i][j].Picture.Bitmap);
      end else
      begin
        CardsObiects[i][j].OnClick := OnPlayerCardClick;
        CardsObiects[i][j].Tag := j;
        CardsObiects[i][j].Cursor := crHandPoint;
        if (Game.CurrDeal.Deal = dBrow) or ((Game.CurrDeal.Deal = dDark) and Game.IsBet) then
          ilBacks.GetBitmap(FSettings.CardBack, CardsObiects[i][j].Picture.Bitmap)
        else begin
          CardsObiects[i][j].ShowHint := true;
          CardsObiects[i][j].Hint := Game.CardToStr(Game.Party[i].Cards[j]);
          case FSettings.DeckType of
            dtRussian: ilDeckRus.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
            dtSolitaire: ilDeckSol.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
            dtSlav: ilDeckSlav.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
            dtSouvenir: ilDeckSouv.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
            dtEnglish: ilDeckEng.GetBitmap(Ord(Game.Party[i].Cards[j]), CardsObiects[i][j].Picture.Bitmap);
          end;
        end;
      end;
    end;
  end;

  imTrump.Picture.Assign(nil);
  ilLear.GetBitmap(Ord(Game.Trump), imTrump.Picture.Bitmap);
  imTrump.Hint := 'Козырь: ' + Game.LearToStr(Game.Trump, 'Бескозырка');

  imTblCard1.Picture.Assign(nil);
  imTblCard2.Picture.Assign(nil);
  imTblCard3.Picture.Assign(nil);
  imTblCard1.Hint := '';
  imTblCard2.Hint := '';
  imTblCard3.Hint := '';
  lbTableCard1.Caption := '';
  lbTableCard2.Caption := '';
  lbTableCard3.Caption := '';
  for i := 0 to Length(Game.TableCards) - 1 do
  begin
    case i of
      0:
      begin
        im := imTblCard1;
        lb := lbTableCard1;
      end;
      1:
      begin
        im := imTblCard2;
        lb := lbTableCard2;
      end;
      2:
      begin
        im := imTblCard3;
        lb := lbTableCard3;
      end;
      else break;
    end;

    lb.Caption := Game.Player[Game.TableCards[i].Player].Name;
    im.Hint := Game.Player[Game.TableCards[i].Player].Name + ': ' + Game.CardToStr(Game.TableCards[i].Card);
    if Game.TableCards[i].Card in [cJoker1, cJoker2] then
      im.Hint := im.Hint + ': ' + Game.JokerActionToStr(Game.TableCards[i].JokerAction, Game.TableCards[i].JokerCard);
        
    case FSettings.DeckType of
      dtRussian: ilDeckRus.GetBitmap(Ord(Game.TableCards[i].Card), im.Picture.Bitmap);
      dtSolitaire: ilDeckSol.GetBitmap(Ord(Game.TableCards[i].Card), im.Picture.Bitmap);
      dtSlav: ilDeckSlav.GetBitmap(Ord(Game.TableCards[i].Card), im.Picture.Bitmap);
      dtSouvenir: ilDeckSouv.GetBitmap(Ord(Game.TableCards[i].Card), im.Picture.Bitmap);
      dtEnglish: ilDeckEng.GetBitmap(Ord(Game.TableCards[i].Card), im.Picture.Bitmap);
    end;
  end;
  Application.ProcessMessages;
end;

procedure TFMain.SaveWndState;
begin
  FSettings.WMaximized := WindowState = wsMaximized;
  if not FSettings.WMaximized then
  begin
    FSettings.WTop := Top;
    FSettings.WLeft := Left;
    FSettings.WWidth := Width;
    FSettings.WHeight := Height;
  end;
end;

procedure TFMain.SetDbgMode(const Value: boolean);
begin
  if Game.Started and (Game.GameType <> gtLocal) then FDbgMode := false
  else FDbgMode := Value;
  
  if FDbgMode then
  begin
    if FSettings.FirstDbgMode then FSettings.FirstDbgMode := false;
    FSettings.KeepLog := true;
    StatusBar.Panels[2].Text := '   -= ! РЕЖИМ ОТЛАДКИ ! =-';
  end else
    StatusBar.Panels[2].Text := '';

  if Game.Started then
  begin
    btnSkipDeal.Visible := FDbgMode;
    DrawObjects(false);
  end;
end;

procedure TFMain.SetMessage(Target: TMsgLabel; Text: string; Delay: integer; CanClearAll: boolean; ShowMsgBox: boolean);
begin
  if CanClearAll then
  begin
    lbInfo.Caption := '';
    lbPlayer1Order.Caption := '';
    lbPlayer1Take.Caption := '';
    lbPlayer2Order.Caption := '';
    lbPlayer2Take.Caption := '';
    lbPlayer3Order.Caption := '';
    lbPlayer3Take.Caption := '';
  end;

  case Target of
    lDeal: lbDeal.Caption := Text;
    lInfo: lbInfo.Caption := Text;
    lP1Order: lbPlayer1Order.Caption := Text;
    lP1Take: lbPlayer1Take.Caption := Text;
    lP2Order: lbPlayer2Order.Caption := Text;
    lP2Take: lbPlayer2Take.Caption := Text;
    lP3Order: lbPlayer3Order.Caption := Text;
    lP3Take: lbPlayer3Take.Caption := Text;
  end;
  lbInfo.Left := Round(ClientWidth / 2.5) - Round(lbInfo.Width / 2);
  while (lbInfo.Left + lbInfo.Width > dbgGameData.Left) and (lbInfo.Left > 10) do lbInfo.Left := lbInfo.Left - 10;
  lbDeal.Left := Round(ClientWidth / 2.5) - Round(lbDeal.Width / 2);
  lbPlayer2Order.Left := ClientWidth - lbPlayer2Order.Width - 10;
  lbPlayer2Take.Left := ClientWidth - lbPlayer2Take.Width - 10;

  Application.ProcessMessages;

  if ShowMsgBox and FSettings.ShowGameMessages then ShowGameMsg(Application.Title, Text);
  
  if Delay > 0 then
  begin
    Screen.Cursor := crHourGlass;
    Sleep(Delay);
    Screen.Cursor := crDefault;
  end;
end;

procedure TFMain.SetPlayerConsole(SetType: integer);
var
  i, idx: integer;

begin
  {SetType:
    -1 - все спрятать
    0 - показать набор для заказа карт
    1 - показать набор для "Далее" в конце круга - переход к следующему кругу
    2 - показать набор для "Далее" в конце игры - завершить игру
  }
  lbBet.Visible := false;
  cbBet.Visible := false;
  btnNextAction.Visible := false;
  btnSkipDeal.Visible := false;
  case SetType of
    0:
    begin
      if DbgMode then btnSkipDeal.Visible := true;
      lbBet.Visible := true;
      cbBet.Visible := true;
      btnNextAction.Visible := true;
      idx := cbBet.ItemIndex;
      cbBet.Items.Clear;
      for i := 0 to Length(Game.Party[2].Cards) do
        if i = 0 then cbBet.Items.Add('Пас')
        else cbBet.Items.Add(IntToStr(i));
      cbBet.DropDownCount := Length(Game.Party[2].Cards) + 1;
      if idx < 0 then cbBet.ItemIndex := 0
      else begin
        while (idx > -1) and (idx > cbBet.Items.Count - 1) do Dec(idx);
        cbBet.ItemIndex := idx;
      end;
      btnNextAction.Caption := 'Заказать';
      cbBet.SetFocus;
    end;
    1:
    begin
      btnNextAction.Visible := true;
      btnNextAction.Caption := 'Далее';
      btnNextAction.SetFocus;
    end;
    2:
    begin
      btnNextAction.Visible := true;
      btnNextAction.Caption := 'Завершить';
      btnNextAction.SetFocus;
    end;
  end;
  Application.ProcessMessages;
end;

procedure TFMain.ShowGameControls(AShow: boolean);
begin
  dbgGameData.Visible := AShow;

  pFace1.Visible := AShow;
  lbPlayer1.Visible := AShow;
  lbPlayer1Order.Visible := AShow;
  lbPlayer1Take.Visible := AShow;

  pFace2.Visible := AShow;
  lbPlayer2.Visible := AShow;
  lbPlayer2Order.Visible := AShow;
  lbPlayer2Take.Visible := AShow;

  pFace3.Visible := AShow;
  lbPlayer3.Visible := AShow;
  lbPlayer3Order.Visible := AShow;
  lbPlayer3Take.Visible := AShow;

  pTrump.Visible := AShow;
  bvTable.Visible := AShow;
  pTblCard1.Visible := AShow;
  pTblCard2.Visible := AShow;
  pTblCard3.Visible := AShow;
  lbTableCard1.Visible := AShow;
  lbTableCard2.Visible := AShow;
  lbTableCard3.Visible := AShow;
  lbInfo.Visible := AShow;
  lbDeal.Visible := AShow;
  btnSkipDeal.Visible := AShow and DbgMode;

  if not AShow then
  begin
    lbBet.Visible := false;
    cbBet.Visible := false;
    btnNextAction.Visible := false;
  end;
  Application.ProcessMessages;
end;

function TFMain.ShowGameMsg(ACaption, AMessage: string; Flags: integer): boolean;
var
  mb: TFGameMsg;

begin
  mb := TFGameMsg.Create(self);
  try
    if not FSettings.ShowGameMessages then exit;
    mb.Caption := ACaption;
    mb.lbMessage.Caption := AMessage;
    mb.tmrAutoHide.Interval := FSettings.AutoHideMsg * 1000;
    mb.tmrAutoHide.Enabled := FSettings.AutoHideMsg > 0;
    case Flags of
      0:
      begin
        result := true;
        mb.btnCancel.Visible := false;
        mb.btnSave.Left := mb.btnCancel.Left;
        mb.ShowModal;
      end;
      1: result := mb.ShowModal = mrOk;
      else result := false;
    end;
    FSettings.ShowGameMessages := not mb.chbNoShow.Checked;
  finally
    mb.Free;
  end;
end;

procedure TFMain.ShowPlayerInfo(pIdx: integer);
var
  FEditRobot: TFRobotParams;
  FEditHuman: TFHumanParams;

begin
  if Game.Player[pIdx].Control = ctRobot then
  begin
    FEditRobot := TFRobotParams.Create(self);
    FEditRobot.GroupBox1.Enabled := false;
    FEditRobot.btnSave.Visible := false;
    FEditRobot.edName.Text := Game.Player[pIdx].Name;
    FEditRobot.cbDifficulty.ItemIndex := Ord(Game.Player[pIdx].Difficulty);
    FEditRobot.cbBehavior.ItemIndex := Ord(Game.Player[pIdx].Behavior);
    FEditRobot.cbPlayStyle.ItemIndex := Ord(Game.Player[pIdx].PlayStyle);
    FEditRobot.FaceFile := FSettings.DataDir + USER_DATA_DIR + Game.Player[pIdx].FaceFile;
    if FileExists(FEditRobot.FaceFile) then
      try
        FEditRobot.imFace.Picture.LoadFromFile(FEditRobot.FaceFile);
      except
      end;

    FEditRobot.ShowModal;
  end else
  begin
    FEditHuman := TFHumanParams.Create(self);
    FEditHuman.GroupBox1.Enabled := false;
    FEditHuman.btnSave.Visible := false;
    FEditHuman.edName.Text := Game.Player[pIdx].Name;
    FEditHuman.edPassword.Text := Game.Player[pIdx].Password;
    FEditHuman.edConfirmPass.Text := Game.Player[pIdx].Password;
    FEditHuman.FaceFile := FSettings.DataDir + USER_DATA_DIR + Game.Player[pIdx].FaceFile;
    if FileExists(FEditHuman.FaceFile) then
      try
        FEditHuman.imFace.Picture.LoadFromFile(FEditHuman.FaceFile);
      except
      end;

    FEditHuman.ShowModal;
  end;
end;

procedure TFMain.StartGame;
var
  FSelPlayer: TFSelPlayer;
  pl: string;
  loaded, canRun, p: boolean;
  i, c: integer;
  
begin
  if Game.Started then exit;
  Game.ClearParty;

  c := 0;
  p := false;
  for i := 0 to Length(Game.Players) - 1 do
    if Game.Players[i].Control = ctHumanLocal then p := true
    else Inc(c);

  if not p then
  begin
    Application.MessageBox('В списке игроков нет ни одного человека!', 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  FSelPlayer := TFSelPlayer.Create(self);
  try
    if FSelPlayer.Execute(Game.Players, pl) then
    begin
      p := false;
      if FSelPlayer.chbNetwork.Checked then
      begin
        if FSelPlayer.rbnServer.Checked then InitializeGame(gtServer)
        else InitializeGame(gtClient);
      end else
        InitializeGame(gtLocal);

      case Game.GameType of
        gtLocal:
        begin
          if c < 2 then
          begin
            Application.MessageBox('В списке игроков недостаточно соперников для начала игры.', 'Ошибка', MB_OK + MB_ICONERROR);
            exit;
          end;

          if FileExists(Game.DataDir + Format(SAVE_FILE, [pl])) then
          begin
            if (Application.MessageBox('У вас есть отложенная игра. Хотите доиграть?', 'Начать игру',
              MB_YESNO + MB_ICONQUESTION) = ID_YES) then loaded := Game.LoadGame(pl)
            else p := true;
          end;

          if not loaded then canRun := FStartDialog.Execute(pl, Game)
          else canRun := loaded;
        end;

        gtServer, gtClient:
        begin
          Game.Close;
          Game.Open(pl);
          
          if Game.Active then
          begin
            canRun := FStartDialog.Execute(pl, Game);
            loaded := FStartDialog.IsGameLoaded;
          end else
            Application.MessageBox(pchar(string(iif(Game.GameType = gtClient, 'Не удалось подключиться к серверу ' +
              Game.Host + '!', 'Не удалось создать сервер!')) + ' Ошибка:'#13#10 + Game.LastMessage),
              'Ошибка', MB_OK + MB_ICONERROR);
        end;
      end;

      try
        if canRun then
        begin
          if Game.GameType in [gtServer, gtClient] then DbgMode := false;
          tmrGameTime.Enabled := true;
          FSettings.SaveToFile;

          dbgGameData.Columns[1].Title.Caption := Game.Player[0].Name + '|' + 'Зак';
          dbgGameData.Columns[2].Title.Caption := Game.Player[0].Name + '|' + 'Вз';
          dbgGameData.Columns[3].Title.Caption := Game.Player[0].Name + '|' + 'Счет';
          dbgGameData.Columns[4].Title.Caption := Game.Player[1].Name + '|' + 'Зак';
          dbgGameData.Columns[5].Title.Caption := Game.Player[1].Name + '|' + 'Вз';
          dbgGameData.Columns[6].Title.Caption := Game.Player[1].Name + '|' + 'Счет';
          dbgGameData.Columns[7].Title.Caption := Game.Player[2].Name + '|' + 'Зак';
          dbgGameData.Columns[8].Title.Caption := Game.Player[2].Name + '|' + 'Вз';
          dbgGameData.Columns[9].Title.Caption := Game.Player[2].Name + '|' + 'Счет';

          if not loaded then
          begin
            Game.Deck := FSettings.Deck;
            Game.GameOptions := FSettings.GameOptions;
            Game.NoJoker := FSettings.NoJoker;
            Game.StrongJoker := FSettings.StrongJoker;
            Game.JokerMajorLear := FSettings.JokerMajorLear;
            Game.JokerMinorLear := FSettings.JokerMinorLear;
            Game.MultDark := FSettings.MultDark;
            Game.MultBrow := FSettings.MultBrow;
            Game.PassPoints := FSettings.PassPoints;
            Game.LongGame := FSettings.LongGame;
            Game.PenaltyMode := FSettings.PenaltyMode;
            DrawObjects(true);
            Game.StartGame(p);
          end;
        end;
      finally
        if (not Game.Started) then Game.Close(true);
      end;
    end;
  finally
    FSelPlayer.Free;
  end;
end;

procedure TFMain.StopGame(AHold: boolean);
var
  s: string;

begin
  if not Game.CanStopGame then
  begin
    if AHold then s := 'Отложить партию? Вы сможете продолжить отложенную партию позже.'
    else s := 'Бросить партию? Все данные текущей партии будут потеряны!';

    if (Application.MessageBox(pchar(s), 'Подтверждение', MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;
    if AHold then Game.HoldGame
    else Game.StopGame(false);
  end else
    Game.StopGame(true);

  ShowGameControls(false);
  FreeGameObjects;
  tmrGameTime.Enabled := false;
  StatusBar.Panels[0].Text := '';
end;

procedure TFMain.tmrGameTimeTimer(Sender: TObject);
begin
  StatusBar.Panels[0].Text := TimeToStr(Now - Game.GameTime);
end;

procedure TFMain.tmrStartTimer(Sender: TObject);
begin
  tmrStart.Enabled := false;
  AStartGameExecute(AStartGame);
end;

procedure TFMain.TrayIconClick(Sender: TObject);
begin
  Show;
end;

end.
