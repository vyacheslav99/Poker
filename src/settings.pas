unit settings;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms, Dialogs, utils, IniFiles, StdCtrls, Buttons,
  ExtCtrls, ComCtrls, Mask, JvExMask, JvToolEdit, Spin, JvBackgrounds, example, engine;

type
  TFSettings = class(TForm)
    btnReset: TBitBtn;
    btnSave: TBitBtn;
    btnCancel: TBitBtn;
    PageControl1: TPageControl;
    tsInterface: TTabSheet;
    Label25: TLabel;
    cbBgColor: TColorBox;
    Label4: TLabel;
    Label5: TLabel;
    tsBehavior: TTabSheet;
    GroupBox1: TGroupBox;
    Label1: TLabel;
    Label2: TLabel;
    Label3: TLabel;
    cbEscAction: TComboBox;
    edEscSetCaption: TEdit;
    edEscSetIcon: TJvFilenameEdit;
    Label6: TLabel;
    cbDeckType: TComboBox;
    lwBack: TListView;
    OpenDialog: TOpenDialog;
    GroupBox2: TGroupBox;
    Label7: TLabel;
    rbnSortAsc: TRadioButton;
    rbnSortDesc: TRadioButton;
    Label8: TLabel;
    rbnNoSort: TRadioButton;
    lbLearOrder: TListBox;
    btnLearUp: TSpeedButton;
    btnLearDown: TSpeedButton;
    bntCreateShortcut: TBitBtn;
    btnSetFont: TBitBtn;
    Label30: TLabel;
    FontDialog: TFontDialog;
    Label9: TLabel;
    edWaitDelay: TSpinEdit;
    tsTable: TTabSheet;
    Label10: TLabel;
    cbGridTitleBgColor: TColorBox;
    Label11: TLabel;
    cbGridTitleFontColor: TColorBox;
    Label12: TLabel;
    cbGridBgColor: TColorBox;
    Label13: TLabel;
    cbGridFontColor: TColorBox;
    Label14: TLabel;
    cbGridBgTakeColor: TColorBox;
    Label15: TLabel;
    cbGridBgDealColor: TColorBox;
    Label16: TLabel;
    cbGridBgScoresColor: TColorBox;
    Label17: TLabel;
    cbGridFontDealColor: TColorBox;
    Label18: TLabel;
    cbGridFontTakeColor: TColorBox;
    Label19: TLabel;
    cbGridFontScoresColor: TColorBox;
    chbKeepLog: TCheckBox;
    tsProfile: TTabSheet;
    Label20: TLabel;
    cbProfile: TComboBox;
    btnAddProfile: TSpeedButton;
    btnDelProfile: TSpeedButton;
    btnRename: TSpeedButton;
    chbSaveEachStep: TCheckBox;
    chbAutoStart: TCheckBox;
    chbShowMessages: TCheckBox;
    Label21: TLabel;
    edAutoHideGameMsg: TSpinEdit;
    tsNetwork: TTabSheet;
    Label22: TLabel;
    edPortNumber: TSpinEdit;
    lbPortDescr: TLabel;
    lbPort: TLabel;
    pExample: TPanel;
    cbBgImage: TComboBox;
    frmExample: TfrmExample;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure btnResetClick(Sender: TObject);
    procedure btnSaveClick(Sender: TObject);
    procedure btnCancelClick(Sender: TObject);
    procedure lbLearOrderDrawItem(Control: TWinControl; Index: Integer; Rect: TRect; State: TOwnerDrawState);
    procedure btnLearUpClick(Sender: TObject);
    procedure bntCreateShortcutClick(Sender: TObject);
    procedure btnSetFontClick(Sender: TObject);
    procedure btnAddProfileClick(Sender: TObject);
    procedure btnDelProfileClick(Sender: TObject);
    procedure btnRenameClick(Sender: TObject);
    procedure cbProfileChange(Sender: TObject);
    procedure edPortNumberChange(Sender: TObject);
    procedure cbBgImageChange(Sender: TObject);
  private
    r_ok: boolean;
    FAppDir: string;
    FSetFileName: string;
    procedure SetToControls;
    procedure GetFromControls;
    procedure FillBgImages;
    procedure FillBackImages;
    procedure CreateLearsDefOrder;
    procedure AddLear(Index: integer; Lear: TLearName);
    function GameOptionsToStr(GameOpts: TGameOptions): string;
    function GameOptionsFromStr(GameOpts: string): TGameOptions;
    function GetDataDir: string;
    procedure DelProfile;
    procedure SaveProfile;
  public
    //параметры программы
    FirstDbgMode: boolean;
    Profile: integer;
    EscAction: TEscHideAction;
    EscSetCaption: string;
    EscSetIcon: string;
    TableBg: integer;
    TableBgFile: string;
    TableBgColor: TColor;
    CardBack: integer;
    DeckType: TDeckType;
    //SeparateLear: boolean;
    SortDirection: TSortDirection;
    LearOrder: TLearList;
    AutoStart: boolean;
    ScrFont: TFont;
    WaitDelay: integer;
    KeepLog: boolean;
    SaveEachStep: boolean;
    ShowGameMessages: boolean;
    AutoHideMsg: integer;
    // настройки таблицы
    GridTitleBgColor: TColor;
    GridTitleFontColor: TColor;
    GridBgColor: TColor;
    GridFontColor: TColor;
    GridBgDealColor: TColor;
    GridFontDealColor: TColor;
    GridBgTakeColor: TColor;
    GridFontTakeColor: TColor;
    GridBgScoresColor: TColor;
    GridFontScoresColor: TColor;
    // настройки размеров и позиций, к-рые нельзя менять (они сохраняются автоматически)
    WLeft: integer;
    WTop: integer;
    WWidth: integer;
    WHeight: integer;
    WMaximized: boolean;
    ChartMarksVisible: boolean;
    // параметры игры
    LastPartnerLeft: string;
    LastPartnerRight: string;
    LastPlayer: string;
    GameOptions: TGameOptions;
    Deck: TDeckSize;
    NoJoker: boolean;
    StrongJoker: boolean;
    JokerMajorLear: boolean;
    JokerMinorLear: boolean;
    MultDark: integer;
    MultBrow: integer;
    PassPoints: integer;
    LongGame: boolean;
    PenaltyMode: integer;
    // Ссеть
    ServerIp: string;
    PortNumber: integer;
    ExtraPortNumber: integer;
    UseExtraPortNumber: boolean;
    PingInterval: integer;
    AttemptConnectCount: integer;
    AttemptConnectInterval: Cardinal;
    // системные
    CacheEnabled: boolean;
    function GetCurrProfile: string;
    procedure SetDefault;
    procedure SaveToFile;
    procedure LoadFromFile;
    procedure ResetSettings;
    procedure SetProfile(Index: integer);
    function GetLearOrder: TLearOrder;
    property SettingsFile: string read FSetFileName;
    property DataDir: string read GetDataDir;
  end;

var
  FSettings: TFSettings;

implementation

{$R *.dfm}

uses main;

{ TFSettings }

procedure TFSettings.AddLear(Index: integer; Lear: TLearName);
var
  ico: TIcon;

begin
  ico := TIcon.Create;
  FMain.ilLear.GetIcon(Ord(Lear), ico);
  LearOrder[Index] := TLear.Create(Lear, ico);
  ico.Free;
end;

procedure TFSettings.bntCreateShortcutClick(Sender: TObject);
begin
  CreateLink(Application.ExeName, GetDesktopDir, 'Расписной покер', '');
  Application.MessageBox('Ярлык создан', 'Сообщение', MB_OK + MB_ICONINFORMATION);
end;

procedure TFSettings.btnAddProfileClick(Sender: TObject);
var
  p: string;

begin
  p := Trim(InputBox('Новый профиль', 'Введите имя нового профиля', ''));
  if (p = '') then exit;
  if cbProfile.Items.IndexOf(p) > -1 then
  begin
    Application.MessageBox(pchar('Профиль "' + p + '" уже есть!'), 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  cbProfile.Items.Add(p);
  cbProfile.ItemIndex := cbProfile.Items.Count - 1;
  SetProfile(cbProfile.ItemIndex);
end;

procedure TFSettings.btnCancelClick(Sender: TObject);
begin
  Close;
end;

procedure TFSettings.btnDelProfileClick(Sender: TObject);
begin
  if cbProfile.ItemIndex = 0 then
  begin
    Application.MessageBox('Невозможно удалить стандартный профиль!', 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  if (Application.MessageBox(pchar('Удалить профиль "' + cbProfile.Text + '"? Все настройки, заданные в этом профиле, будут потеряны!'),
    'Подтверждение', MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;

  DelProfile;
end;

procedure TFSettings.btnLearUpClick(Sender: TObject);
var
  i: integer;

begin
  if lbLearOrder.ItemIndex = -1 then exit;
  if TSpeedButton(Sender) = btnLearUp then
  begin
    if lbLearOrder.ItemIndex = 0 then exit
    else i := lbLearOrder.ItemIndex - 1;
  end else if TSpeedButton(Sender) = btnLearDown then
  begin
    if lbLearOrder.ItemIndex = (lbLearOrder.Count - 1) then exit
    else i := lbLearOrder.ItemIndex + 1;
  end else exit;

  lbLearOrder.Items.Exchange(lbLearOrder.ItemIndex, i);
end;

procedure TFSettings.btnRenameClick(Sender: TObject);
var
  p: string;
  i: integer;
  
begin
  if cbProfile.ItemIndex = 0 then
  begin
    Application.MessageBox('Невозможно переименовать стандартный профиль!', 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  i := cbProfile.ItemIndex;
  p := Trim(InputBox('Переименовать профиль', 'Введите новое имя профиля', cbProfile.Items.Strings[i]));
  if (p = '') or (p = cbProfile.Items.Strings[i]) then exit;
  if (cbProfile.Items.IndexOf(p) > -1) and (AnsiLowerCase(p) <> AnsiLowerCase(cbProfile.Items.Strings[i])) then
  begin
    Application.MessageBox(pchar('Профиль "' + p + '" уже есть!'), 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  cbProfile.Items.Strings[i] := p;
  cbProfile.ItemIndex := i;
  SaveProfile;
end;

procedure TFSettings.btnResetClick(Sender: TObject);
begin
  ResetSettings;
end;

procedure TFSettings.btnSaveClick(Sender: TObject);
begin
  r_ok := true;
  Close;
end;

procedure TFSettings.btnSetFontClick(Sender: TObject);
begin
  FontDialog.Font.Assign(ScrFont);
  if FontDialog.Execute then
  begin
    ScrFont.Assign(FontDialog.Font);
    cbBgImageChange(cbBgImage);
  end;
end;

procedure TFSettings.cbBgImageChange(Sender: TObject);
var
  s: string;
  
begin
  frmExample.lbExample.Font.Assign(ScrFont);
  frmExample.lbExample.Caption := cbBgImage.Text;
  pExample.Color := cbBgColor.Selected;
  frmExample.Color := cbBgColor.Selected;
  if cbBgImage.ItemIndex = 0 then
  begin
    pExample.ParentBackground := false;
    frmExample.bgImageExample.Image.Picture.Bitmap.Assign(nil)
  end else
  begin
    pExample.ParentBackground := true;
    s := FSettings.DataDir + BG_DIR + cbBgImage.Items[cbBgImage.ItemIndex];
    if FileExists(s) then
      frmExample.bgImageExample.Image.Picture.LoadFromFile(s)
    else begin
      pExample.ParentBackground := false;
      frmExample.bgImageExample.Image.Picture.Bitmap.Assign(nil);
      frmExample.lbExample.Caption := 'Не найден файл!'#13#10 + BG_DIR + cbBgImage.Text;
      frmExample.lbExample.Hint := BG_DIR + cbBgImage.Text;
      frmExample.lbExample.Font.Color := clRed;
      frmExample.lbExample.Font.Size := 8;
      frmExample.lbExample.Font.Style := [];
    end;
  end;
end;

procedure TFSettings.cbProfileChange(Sender: TObject);
begin
  SetProfile(cbProfile.ItemIndex);
end;

procedure TFSettings.FillBackImages;
var
  i: integer;

begin
  lwBack.Items.Clear;
  for i := 0 to FMain.ilBacks.Count - 1 do
  begin
    lwBack.Items.Add;
    lwBack.Items.Item[i].ImageIndex := i;
  end;
end;

procedure TFSettings.FillBgImages;
var
  sr: TSearchRec;
  si: integer;
  src: string;

begin
  cbBgImage.Items.Clear;
  cbBgImage.Items.Add('< НЕТ >');

  src := DataDir + BG_DIR;
  if not ForceDirectories(src) then exit;

  si := FindFirst(src + '*.bmp', faAnyFile, sr);
  while si = 0 do
  begin
    if (sr.Name = '.') or (sr.Name = '..') or ((sr.Attr and faDirectory) = faDirectory) then
    begin
      si := FindNext(sr);
      continue;
    end;

    cbBgImage.Items.Add(sr.Name);
    si := FindNext(sr);
  end;

  FindClose(sr);
end;

procedure TFSettings.CreateLearsDefOrder;
var
  i: TLearName;

begin
  for i := lnHearts to lnSpades do AddLear(Ord(i), i);
end;

procedure TFSettings.DelProfile;
begin
  cbProfile.Items.Delete(Profile);
  cbProfile.ItemIndex := 0;
  SetProfile(cbProfile.ItemIndex);
end;

procedure TFSettings.edPortNumberChange(Sender: TObject);
begin
  try
    lbPortDescr.Caption := CheckPortNumber(edPortNumber.Value);
  except
    exit;
  end;

  if lbPortDescr.Caption = '' then
  begin
    lbPort.Caption := 'Свободен';
    lbPort.Font.Color := clGreen;
  end else
  begin
    lbPort.Caption := 'Занят:';
    lbPort.Font.Color := clMaroon;
  end;
end;

procedure TFSettings.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  if r_ok then
  begin
    ModalResult := mrOk;
    GetFromControls;
    SaveToFile;
  end else
    ModalResult := mrCancel;

  Action := caHide;
end;

procedure TFSettings.FormCreate(Sender: TObject);
begin
  FAppDir := ExtractFilePath(Application.ExeName);
  ScrFont := TFont.Create;
  FillBgImages;
  FillBackImages;
  FSetFileName := DataDir + PARAM_FILE;
  ForceDirectories(DataDir);
  LoadFromFile;
  PageControl1.ActivePageIndex := 0;
end;

procedure TFSettings.FormDestroy(Sender: TObject);
begin
  SaveToFile;
  ScrFont.Free;
end;

procedure TFSettings.FormShow(Sender: TObject);
begin
  r_ok := false;
  SetToControls;
end;

function TFSettings.GameOptionsFromStr(GameOpts: string): TGameOptions;
var
  i: integer;

begin
  result := [];
  try
    for i := 1 to WordCountEx(GameOpts, [','], []) do
      result := result + [TGameOption(StrToInt(ExtractWordEx(i, GameOpts, [','], [])))];
  except
    result := [goAsc, goDesc, goEven, goNotEven, goNoTrump, goDark, goGold, goMizer, goBrow];
  end;
end;

function TFSettings.GameOptionsToStr(GameOpts: TGameOptions): string;
var
  i: TGameOption;

begin
  result := '';
  for i := Low(i) to High(i) do
    if i in GameOpts then
    begin
      if result = '' then result := IntToStr(Ord(i))
      else result := result + ',' + IntToStr(Ord(i));
    end;
end;

function TFSettings.GetCurrProfile: string;
begin
  result := '.' + Trim(cbProfile.Items.Strings[Profile]);
  if result = '.' then result := '.' + DEF_PROFILE;
end;

function TFSettings.GetDataDir: string;
begin
  result := FAppDir + DATA_DIR;
end;

procedure TFSettings.GetFromControls;
var
  i: integer;
  
begin
  Profile := cbProfile.ItemIndex;
  TableBgColor := cbBgColor.Selected;
  TableBg := cbBgImage.ItemIndex;
  TableBgFile := cbBgImage.Items[TableBg];
  DeckType := TDeckType(cbDeckType.ItemIndex);
  CardBack := lwBack.ItemIndex;
  EscAction := TEscHideAction(cbEscAction.ItemIndex);
  EscSetCaption := edEscSetCaption.Text;
  EscSetIcon := edEscSetIcon.FileName;
  //SeparateLear := chbSeparateLear.Checked;
  if rbnNoSort.Checked then SortDirection := sdNone
  else if rbnSortAsc.Checked then SortDirection := sdAsc
  else if rbnSortDesc.Checked then SortDirection := sdDesc;
  for i := 0 to Length(LearOrder) - 1 do
    LearOrder[i] := TLear(lbLearOrder.Items.Objects[i]);
  AutoStart := chbAutoStart.Checked;
  WaitDelay := edWaitDelay.Value;
  GridTitleBgColor := cbGridTitleBgColor.Selected;
  GridTitleFontColor := cbGridTitleFontColor.Selected;
  GridBgColor := cbGridBgColor.Selected;
  GridFontColor := cbGridFontColor.Selected;
  GridBgDealColor := cbGridBgDealColor.Selected;
  GridFontDealColor := cbGridFontDealColor.Selected;
  GridBgTakeColor := cbGridBgTakeColor.Selected;
  GridFontTakeColor := cbGridFontTakeColor.Selected;
  GridBgScoresColor := cbGridBgScoresColor.Selected;
  GridFontScoresColor := cbGridFontScoresColor.Selected;
  KeepLog := chbKeepLog.Checked;
  SaveEachStep := chbSaveEachStep.Checked;
  ShowGameMessages := chbShowMessages.Checked;
  AutoHideMsg := edAutoHideGameMsg.Value;
  PortNumber := edPortNumber.Value;
end;

function TFSettings.GetLearOrder: TLearOrder;
var
  i: integer;

begin
  for i := 0 to Length(LearOrder) - 1 do result[i] := LearOrder[i].Lear;
end;

procedure TFSettings.lbLearOrderDrawItem(Control: TWinControl; Index: Integer; Rect: TRect; State: TOwnerDrawState);
var
  offs: integer;

begin
  if (TListBox(Control).Items.Objects[Index] <> nil) and Assigned(TListBox(Control).Items.Objects[Index]) then
  begin
    TListBox(Control).Canvas.FillRect(Rect);
    TListBox(Control).Canvas.Draw(Rect.Left + 1, Rect.Top + 2, TLear(TListBox(Control).Items.Objects[Index]).Icon);
    offs := TLear(TListBox(Control).Items.Objects[Index]).Icon.Width + 9;
    TListBox(Control).Canvas.TextOut(Rect.Left + offs, Rect.Top + 2, TLear(TListBox(Control).Items.Objects[Index]).LearName);
  end;
end;

procedure TFSettings.LoadFromFile;
var
  fs: TIniFile;
  i: integer;

begin
  try
    fs := TIniFile.Create(FSetFileName);

    cbProfile.Items.Text := StringReplace(fs.ReadString(INI_SEC_PROFILES, 'ProfilesList', DEF_PROFILE), REC_WORD_DELIM, #13#10, [rfReplaceAll]);
    if cbProfile.Items.IndexOf(DEF_PROFILE) > 0 then
    begin
      cbProfile.Items.Delete(cbProfile.Items.IndexOf(DEF_PROFILE));
      cbProfile.Items.Insert(0, DEF_PROFILE);
    end;
    Profile := fs.ReadInteger(INI_SEC_PROFILES, 'Current', 0);

    CacheEnabled := fs.ReadBool(INI_SEC_SYSTEM, 'CacheEnabled', true);
    
    WWidth := fs.ReadInteger(INI_SEC_WINDOW, 'mainwidth', 950);
    WHeight := fs.ReadInteger(INI_SEC_WINDOW, 'mainheight', 750);
    WLeft := fs.ReadInteger(INI_SEC_WINDOW, 'mainleft', Round(Screen.Width / 2) - Round(WWidth / 2));
    WTop := fs.ReadInteger(INI_SEC_WINDOW, 'maintop', Round(Screen.Height / 2) - Round(WHeight / 2));
    WMaximized := fs.ReadBool(INI_SEC_WINDOW, 'mainmaximized', false);
    ChartMarksVisible := fs.ReadBool(INI_SEC_WINDOW, 'ChartMarksVisible', false);

    EscAction := TEscHideAction(fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'EscAction', 0));
    EscSetCaption := fs.ReadString(INI_SEC_CONFIG + GetCurrProfile, 'EscSetCaption', '');
    EscSetIcon := fs.ReadString(INI_SEC_CONFIG + GetCurrProfile, 'EscSetIcon', '');
    TableBg := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'TableBg', 1);
    TableBgFile := fs.ReadString(INI_SEC_CONFIG + GetCurrProfile, 'TableBgFile', '0default.bmp');
    TableBgColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'TableBgColor', clGreen);
    CardBack := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'CardBack', 6);
    DeckType := TDeckType(fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'DeckType', 0));
    //SeparateLear := fs.ReadBool(INI_SEC_CONFIG + GetCurrProfile, 'SeparateLear', false);
    SortDirection := TSortDirection(fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'SortDirection', 0));
    AutoStart := fs.ReadBool(INI_SEC_CONFIG + GetCurrProfile, 'AutoStart', false);
    ScrFont.Name := fs.ReadString(INI_SEC_CONFIG + GetCurrProfile, 'Font.Name', 'Tahoma');
    ScrFont.Style := GetFontStyle(fs.ReadString(INI_SEC_CONFIG + GetCurrProfile, 'Font.Style', 'fsBold'));
    ScrFont.Size := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'Font.Size', 10);
    ScrFont.Color := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'Font.Color', clWhite);
    WaitDelay := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'WaitDelay', 0);
    GridTitleBgColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridTitleBgColor', clCream);
    GridTitleFontColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridTitleFontColor', clMaroon);
    GridBgColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridBgColor', clTeal);
    GridFontColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridFontColor', clYellow);
    GridBgDealColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridBgDealColor', clNavy);
    GridFontDealColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridFontDealColor', clYellow);
    GridBgTakeColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridBgTakeColor', clTeal);
    GridFontTakeColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridFontTakeColor', clYellow);
    GridBgScoresColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridBgScoresColor', clGreen);
    GridFontScoresColor := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridFontScoresColor', clAqua);
    KeepLog := fs.ReadBool(INI_SEC_CONFIG + GetCurrProfile, 'KeepLog', false);
    SaveEachStep := fs.ReadBool(INI_SEC_CONFIG + GetCurrProfile, 'SaveEachStep', false);
    FirstDbgMode := fs.ReadBool(INI_SEC_CONFIG + GetCurrProfile, 'FirstDbgMode', true);
    ShowGameMessages := fs.ReadBool(INI_SEC_CONFIG + GetCurrProfile, 'ShowGameMessages', true);
    AutoHideMsg := fs.ReadInteger(INI_SEC_CONFIG + GetCurrProfile, 'AutoHideMsg', 5);

    for i := 0 to 3 do
      AddLear(fs.ReadInteger(INI_SEC_LEAR_ORDER + GetCurrProfile, IntToStr(i), i), TLearName(i));

    LastPartnerLeft := fs.ReadString(INI_SEC_GAME_OPTS + GetCurrProfile, 'LastPartnerLeft', '');
    LastPartnerRight := fs.ReadString(INI_SEC_GAME_OPTS + GetCurrProfile, 'LastPartnerRight', '');
    LastPlayer := fs.ReadString(INI_SEC_GAME_OPTS + GetCurrProfile, 'LastPlayer', '');
    GameOptions := GameOptionsFromStr(fs.ReadString(INI_SEC_GAME_OPTS + GetCurrProfile, 'GameOptions', '4,5,6,7'));
    Deck := TDeckSize(fs.ReadInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'Deck', 0));
    NoJoker := fs.ReadBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'NoJoker', false);
    StrongJoker := fs.ReadBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'StrongJoker', true);
    JokerMajorLear := fs.ReadBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'JokerMajorLear', true);
    JokerMinorLear := fs.ReadBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'JokerMinorLear', true);
    MultDark := fs.ReadInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'MultDark', 2);
    MultBrow := fs.ReadInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'MultBrow', 5);
    PassPoints := fs.ReadInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'PassPoints', 5);
    LongGame := fs.ReadBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'LongGame', false);
    PenaltyMode := fs.ReadInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'PenaltyMode', 0);

    PortNumber := fs.ReadInteger(INI_SEC_NETWORK, 'PortNumber', 21000);
    ExtraPortNumber := fs.ReadInteger(INI_SEC_NETWORK, 'ExtraPortNumber', 21001);
    UseExtraPortNumber := fs.ReadBool(INI_SEC_NETWORK, 'UseExtraPortNumber', false);
    ServerIp := fs.ReadString(INI_SEC_NETWORK, 'ServerIp', '127.0.0.1');
    PingInterval := fs.ReadInteger(INI_SEC_NETWORK, 'PingInterval', 20);
    AttemptConnectCount := fs.ReadInteger(INI_SEC_NETWORK, 'AttemptConnectCount', 3);
    AttemptConnectInterval := fs.ReadInteger(INI_SEC_NETWORK, 'AttemptConnectInterval', 3000);
  except
    on E: Exception do
    begin
      SetDefault;
      Application.MessageBox(pchar('Не удалось прочитать настройки программы! Установлены настройки по-умолчанию.'#13#19 + E.Message),
        'Ошибка', MB_OK + MB_ICONERROR);
    end;
  end;
  if Assigned(fs) then fs.Free;
end;

procedure TFSettings.ResetSettings;
var
  err: string;
  
begin
  if Application.MessageBox('В результате данной операции будут загружены стандартные настройки.'#13 +
    'Вы точно хотите сбросить все настройки?', 'Сброс настроек', MB_YESNO + MB_ICONWARNING) = ID_NO then exit;

  DeleteFile(FSetFileName + '.bak');
  CopyFile(FSetFileName, FSetFileName + '.bak', err);
  DeleteIniSection(FSetFileName, INI_SEC_CONFIG + GetCurrProfile);
  DeleteIniSection(FSetFileName, INI_SEC_LEAR_ORDER + GetCurrProfile);
  DeleteIniSection(FSetFileName, INI_SEC_GAME_OPTS + GetCurrProfile);

  LoadFromFile;
  SetToControls;
  SaveToFile;
  r_ok := true;
  Application.MessageBox(pchar('Установлены стандартные настройки'), 'Сброс настроек', MB_OK + MB_ICONINFORMATION);
end;

procedure TFSettings.SaveProfile;
var
  fs: TIniFile;

begin
  try
    fs := TIniFile.Create(FSetFileName);

    fs.WriteInteger(INI_SEC_PROFILES, 'Current', Profile);
    fs.WriteString(INI_SEC_PROFILES, 'ProfilesList', TextToString(cbProfile.Items.Text, '', REC_WORD_DELIM));
  except
    on E: Exception do
      Application.MessageBox(pchar('Не удалось сохранить профиль!'#13 + E.Message), 'Ошибка', MB_OK + MB_ICONERROR);
  end;
  if Assigned(fs) then fs.Free;
end;

procedure TFSettings.SaveToFile;
var
  fs: TIniFile;
  i: integer;

begin
  try
    fs := TIniFile.Create(FSetFileName);

    fs.WriteInteger(INI_SEC_PROFILES, 'Current', Profile);
    fs.WriteString(INI_SEC_PROFILES, 'ProfilesList', TextToString(cbProfile.Items.Text, '', REC_WORD_DELIM));

    fs.WriteBool(INI_SEC_SYSTEM, 'CacheEnabled', CacheEnabled);

    fs.WriteInteger(INI_SEC_WINDOW, 'mainleft', WLeft);
    fs.WriteInteger(INI_SEC_WINDOW, 'maintop', WTop);
    fs.WriteInteger(INI_SEC_WINDOW, 'mainwidth', WWidth);
    fs.WriteInteger(INI_SEC_WINDOW, 'mainheight', WHeight);
    fs.WriteBool(INI_SEC_WINDOW, 'mainmaximized', WMaximized);
    fs.WriteBool(INI_SEC_WINDOW, 'ChartMarksVisible', ChartMarksVisible);

    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'EscAction', Ord(EscAction));
    fs.WriteString(INI_SEC_CONFIG + GetCurrProfile, 'EscSetCaption', EscSetCaption);
    fs.WriteString(INI_SEC_CONFIG + GetCurrProfile, 'EscSetIcon', EscSetIcon);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'TableBg', TableBg);
    fs.WriteString(INI_SEC_CONFIG + GetCurrProfile, 'TableBgFile', TableBgFile);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'TableBgColor', TableBgColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'CardBack', CardBack);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'DeckType', Ord(DeckType));
    //fs.WriteBool(INI_SEC_CONFIG + GetCurrProfile, 'SeparateLear', SeparateLear);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'SortDirection', Ord(SortDirection));
    fs.WriteBool(INI_SEC_CONFIG + GetCurrProfile, 'AutoStart', AutoStart);
    fs.WriteString(INI_SEC_CONFIG + GetCurrProfile, 'Font.Name', ScrFont.Name);
    fs.WriteString(INI_SEC_CONFIG + GetCurrProfile, 'Font.Style', FontStyleAsString(ScrFont.Style));
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'Font.Size', ScrFont.Size);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'Font.Color', ScrFont.Color);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'WaitDelay', WaitDelay);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridTitleBgColor', GridTitleBgColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridTitleFontColor', GridTitleFontColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridBgColor', GridBgColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridFontColor', GridFontColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridBgDealColor', GridBgDealColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridFontDealColor', GridFontDealColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridBgTakeColor', GridBgTakeColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridFontTakeColor', GridFontTakeColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridBgScoresColor', GridBgScoresColor);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'GridFontScoresColor', GridFontScoresColor);
    fs.WriteBool(INI_SEC_CONFIG + GetCurrProfile, 'KeepLog', KeepLog);
    fs.WriteBool(INI_SEC_CONFIG + GetCurrProfile, 'SaveEachStep', SaveEachStep);
    fs.WriteBool(INI_SEC_CONFIG + GetCurrProfile, 'FirstDbgMode', FirstDbgMode);
    fs.WriteBool(INI_SEC_CONFIG + GetCurrProfile, 'ShowGameMessages', ShowGameMessages);
    fs.WriteInteger(INI_SEC_CONFIG + GetCurrProfile, 'AutoHideMsg', AutoHideMsg);

    for i := 0 to Length(LearOrder) - 1 do
      fs.WriteInteger(INI_SEC_LEAR_ORDER + GetCurrProfile, IntToStr(Ord(LearOrder[i].Lear)), i);

    fs.WriteString(INI_SEC_GAME_OPTS + GetCurrProfile, 'LastPartnerLeft', LastPartnerLeft);
    fs.WriteString(INI_SEC_GAME_OPTS + GetCurrProfile, 'LastPartnerRight', LastPartnerRight);
    fs.WriteString(INI_SEC_GAME_OPTS + GetCurrProfile, 'LastPlayer', LastPlayer);
    fs.WriteString(INI_SEC_GAME_OPTS + GetCurrProfile, 'GameOptions', GameOptionsToStr(GameOptions));
    fs.WriteInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'Deck', Ord(Deck));
    fs.WriteBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'NoJoker', NoJoker);
    fs.WriteBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'StrongJoker', StrongJoker);
    fs.WriteBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'JokerMajorLear', JokerMajorLear);
    fs.WriteBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'JokerMinorLear', JokerMinorLear);
    fs.WriteInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'MultDark', MultDark);
    fs.WriteInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'MultBrow', MultBrow);
    fs.WriteInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'PassPoints', PassPoints);
    fs.WriteBool(INI_SEC_GAME_OPTS + GetCurrProfile, 'LongGame', LongGame);
    fs.WriteInteger(INI_SEC_GAME_OPTS + GetCurrProfile, 'PenaltyMode', PenaltyMode);

    fs.WriteInteger(INI_SEC_NETWORK, 'PortNumber', PortNumber);
    fs.WriteInteger(INI_SEC_NETWORK, 'ExtraPortNumber', ExtraPortNumber);
    fs.WriteBool(INI_SEC_NETWORK, 'UseExtraPortNumber', UseExtraPortNumber);
    fs.WriteString(INI_SEC_NETWORK, 'ServerIp', ServerIp);
    fs.WriteInteger(INI_SEC_NETWORK, 'PingInterval', PingInterval);
    fs.WriteInteger(INI_SEC_NETWORK, 'AttemptConnectCount', AttemptConnectCount);
    fs.WriteInteger(INI_SEC_NETWORK, 'AttemptConnectInterval', AttemptConnectInterval);
  except
    on E: Exception do
      Application.MessageBox(pchar('Не удалось сохранить настройки программы!'#13 + E.Message), 'Ошибка', MB_OK + MB_ICONERROR);
  end;
  if Assigned(fs) then fs.Free;
end;

procedure TFSettings.SetDefault;
begin
  CacheEnabled := true;
  
  Profile := 0;
  WWidth := 950;
  WHeight := 750;
  WLeft := Round(Screen.Width / 2) - Round(WWidth / 2);
  WTop := Round(Screen.Height / 2) - Round(WHeight / 2);
  WMaximized := false;
  ChartMarksVisible := false;

  EscAction := eaNone;
  EscSetCaption := '';
  EscSetIcon := '';
  TableBg := 1;
  TableBgFile := '0default.bmp';
  TableBgColor := clGreen;
  CardBack := 6;
  DeckType := dtRussian;
  //SeparateLear := false;
  SortDirection := sdNone;
  CreateLearsDefOrder;
  AutoStart := false;
  ScrFont.Name := 'Tahoma';
  ScrFont.Style := [fsBold];
  ScrFont.Size := 10;
  ScrFont.Color := clWhite;
  WaitDelay := 0;
  GridTitleBgColor := clCream;
  GridTitleFontColor := clMaroon;
  GridBgColor := clTeal;
  GridFontColor := clYellow;
  GridBgDealColor := clNavy;
  GridFontDealColor := clYellow;
  GridBgTakeColor := clTeal;
  GridFontTakeColor := clYellow;
  GridBgScoresColor := clGreen;
  GridFontScoresColor := clAqua;
  KeepLog := false;
  SaveEachStep := false;
  FirstDbgMode := true;
  ShowGameMessages := true;
  AutoHideMsg := 5;

  LastPartnerLeft := '';
  LastPartnerRight := '';
  LastPlayer := '';
  GameOptions := [goNoTrump, goDark, goGold, goMizer];
  Deck := dsz36;
  NoJoker := false;
  StrongJoker := true;
  JokerMajorLear := true;
  JokerMinorLear := true;
  MultDark := 2;
  MultBrow := 5;
  PassPoints := 5;
  LongGame := false;
  PenaltyMode := 0;

  PortNumber := 21000;
  ExtraPortNumber := 21001;
  UseExtraPortNumber := false;
  ServerIp := '127.0.0.1';
  PingInterval := 20;
  AttemptConnectCount := 3;
  AttemptConnectInterval := 3000;
end;

procedure TFSettings.SetProfile(Index: integer);
begin
  Profile := Index;
  SaveProfile;
  LoadFromFile;
  SetToControls;
end;

procedure TFSettings.SetToControls;
var
  i: integer;

begin
  Caption := 'Настройки: ' + cbProfile.Items.Strings[Profile];
  cbProfile.ItemIndex := Profile;
  cbBgColor.Selected := TableBgColor;
  cbBgImage.ItemIndex := TableBg;
  cbBgImageChange(cbBgImage);
  cbDeckType.ItemIndex := Ord(DeckType);
  lwBack.ItemIndex := CardBack;
  cbEscAction.ItemIndex := Ord(EscAction);
  edEscSetCaption.Text := EscSetCaption;
  edEscSetIcon.FileName := EscSetIcon;
  //chbSeparateLear.Checked := SeparateLear;
  case SortDirection of
    sdNone: rbnNoSort.Checked := true;
    sdAsc: rbnSortAsc.Checked := true;
    sdDesc: rbnSortDesc.Checked := true;
  end;
  lbLearOrder.Clear;
  for i := 0 to Length(LearOrder) - 1 do
    lbLearOrder.AddItem(LearOrder[i].LearName, LearOrder[i]);
  lbLearOrder.ItemIndex := 0;
  chbAutoStart.Checked := AutoStart;
  pExample.Font.Assign(ScrFont);
  edWaitDelay.Value := WaitDelay;
  cbGridTitleBgColor.Selected := GridTitleBgColor;
  cbGridTitleFontColor.Selected := GridTitleFontColor;
  cbGridBgColor.Selected := GridBgColor;
  cbGridFontColor.Selected := GridFontColor;
  cbGridBgDealColor.Selected := GridBgDealColor;
  cbGridFontDealColor.Selected := GridFontDealColor;
  cbGridBgTakeColor.Selected := GridBgTakeColor;
  cbGridFontTakeColor.Selected := GridFontTakeColor;
  cbGridBgScoresColor.Selected := GridBgScoresColor;
  cbGridFontScoresColor.Selected := GridFontScoresColor;
  chbKeepLog.Checked := KeepLog;
  chbSaveEachStep.Checked := SaveEachStep;
  chbShowMessages.Checked := ShowGameMessages;
  edAutoHideGameMsg.Value := AutoHideMsg;
  edPortNumber.Value := PortNumber;
end;

end.
