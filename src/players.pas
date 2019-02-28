unit players;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, utils, MemTableDataEh, Db, DBGridEhGrouping, GridsEh, DBGridEh, MemTableEh, ExtCtrls,
  StdCtrls, Buttons, humanParams, robotParams, settings, querypass, engine, EhLibMTE;

type
  TFPlayers = class(TForm)
    mtPlayers: TMemTableEh;
    dbgPlayers: TDBGridEh;
    dsoPlayers: TDataSource;
    mtPlayersNAME: TStringField;
    mtPlayersROBOT: TIntegerField;
    mtPlayersALL: TIntegerField;
    mtPlayersCOMPLETED: TIntegerField;
    mtPlayersINTERRUPTED: TIntegerField;
    mtPlayersWINNED: TIntegerField;
    mtPlayersFAILED: TIntegerField;
    mtPlayersSCORES: TIntegerField;
    Panel1: TPanel;
    btnAddRobot: TButton;
    btnAddHuman: TButton;
    btnEdit: TButton;
    btnDelete: TButton;
    btnSave: TBitBtn;
    btnCancel: TBitBtn;
    mtPlayersID: TStringField;
    btnResetAllStat: TButton;
    mtPlayersDIFFICULTY: TIntegerField;
    btnResetStatistic: TButton;
    Bevel1: TBevel;
    mtPlayersAVG: TFloatField;
    mtPlayersTOTAL: TIntegerField;
    procedure FormCreate(Sender: TObject);
    procedure btnSaveClick(Sender: TObject);
    procedure btnCancelClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure btnAddRobotClick(Sender: TObject);
    procedure btnEditClick(Sender: TObject);
    procedure btnDeleteClick(Sender: TObject);
    procedure btnResetAllStatClick(Sender: TObject);
    procedure btnResetStatisticClick(Sender: TObject);
    procedure dbgPlayersGetCellParams(Sender: TObject; Column: TColumnEh; AFont: TFont; var Background: TColor; State: TGridDrawState);
    procedure mtPlayersCalcFields(DataSet: TDataSet);
  private
    r_ok: boolean;
    FPlayers: TPlayerList;
    procedure SetPlayers(Value: TPlayerList);
    procedure RefreshTable;
    procedure AddPlayer(robot: boolean);
    procedure EditPlayer;
    procedure DelPlayer;
    function CheckName(var AName: string): boolean;
    procedure ResetAllStatistic;
    procedure ResetStatistic(PIndex: integer = -1);
    function GetPlayerIndex(Name: string): integer;
  public
    property Players: TPlayerList read FPlayers write SetPlayers;
  end;

implementation

{$R *.dfm}

{ TFPlayers }

procedure TFPlayers.AddPlayer(robot: boolean);
var
  FEditRobot: TFRobotParams;
  FEditHuman: TFHumanParams;
  s, {newFn,} err: string;
  newIdx: integer;

begin
  try
    newIdx := -1;
    if robot then
    begin
      FEditRobot := TFRobotParams.Create(self);
      FEditRobot.cbDifficulty.ItemIndex := 1;
      FEditRobot.cbBehavior.ItemIndex := 0;
      FEditRobot.cbPlayStyle.ItemIndex := 0;
      FEditRobot.FaceFile := '';
      if FEditRobot.ShowModal = mrOk then
      begin
        s := FEditRobot.edName.Text;
        if not CheckName(s) then
        begin
          if s = '' then err := 'Имя игрока пустое!'
          else err := 'Игрок "' + s + '" уже есть!';
          Application.MessageBox(pchar(err), 'Ошибка', MB_OK + MB_ICONERROR);
          exit;
        end;

        SetLength(FPlayers, Length(FPlayers) + 1);
        newIdx := High(FPlayers);
        FPlayers[newIdx].Id := GenRandString(5, 16);
        FPlayers[newIdx].Name := s;
        if FEditRobot.FaceFileChanged {and FileExists(FEditRobot.FaceFile)} then
        {begin
          newFn := FSettings.DataDir + USER_DATA_DIR + ExtractFileName(FEditRobot.FaceFile);
          if AnsiLowerCase(newFn) <> AnsiLowerCase(FEditRobot.FaceFile) then
            if not CopyFile(FEditRobot.FaceFile, newFn, err) then
              Application.MessageBox(pchar('Не удалось перенести файл с изображением в папку данных игры. ' +
                'Изображение не задано! Ошибка'#13#10 + err), 'Ошибка', MB_OK + MB_ICONERROR); }

          FPlayers[newIdx].FaceFile := FEditRobot.FaceFile; //ExtractFileName(newFn);
        //end;
        FPlayers[newIdx].Password := '';
        FPlayers[newIdx].Difficulty := TDifficulty(FEditRobot.cbDifficulty.ItemIndex);
        FPlayers[newIdx].Behavior := TPlayerBehavior(FEditRobot.cbBehavior.ItemIndex);
        FPlayers[newIdx].PlayStyle := TPlayerPlayStyle(FEditRobot.cbPlayStyle.ItemIndex);
        FPlayers[newIdx].Control := ctRobot;
      end;
    end else
    begin
      FEditHuman := TFHumanParams.Create(self);
      FEditHuman.FaceFile := '';
      if FEditHuman.ShowModal = mrOk then
      begin
        s := FEditHuman.edName.Text;
        if not CheckName(s) then
        begin
          Application.MessageBox(pchar('Игрок "' + '" уже есть!'), 'Ошибка', MB_OK + MB_ICONERROR);
          exit;
        end;

        SetLength(FPlayers, Length(FPlayers) + 1);
        newIdx := High(FPlayers);
        FPlayers[newIdx].Id := GenRandString(5, 16);
        FPlayers[newIdx].Name := s;
        if FEditHuman.FaceFileChanged {and FileExists(FEditHuman.FaceFile)} then
        {begin
          newFn := FSettings.DataDir + USER_DATA_DIR + ExtractFileName(FEditHuman.FaceFile);
          if AnsiLowerCase(newFn) <> AnsiLowerCase(FEditHuman.FaceFile) then
            if not CopyFile(FEditHuman.FaceFile, newFn, err) then
              Application.MessageBox(pchar('Не удалось перенести файл с изображением в папку данных игры. ' +
                'Изображение не задано! Ошибка'#13#10 + err), 'Ошибка', MB_OK + MB_ICONERROR); }

          FPlayers[newIdx].FaceFile := FEditHuman.FaceFile; //ExtractFileName(newFn);
        //end;
        FPlayers[newIdx].Password := Trim(FEditHuman.edPassword.Text);
        FPlayers[newIdx].Difficulty := dfUndefined;
        FPlayers[newIdx].Behavior := ubNormal;
        FPlayers[newIdx].PlayStyle := psForSelf;
        FPlayers[newIdx].Control := ctHumanLocal;
      end;
    end;

    if newIdx > -1 then
    begin
      FPlayers[newIdx].cAll := 0;
      FPlayers[newIdx].cCompleted := 0;
      FPlayers[newIdx].cInterrupted := 0;
      FPlayers[newIdx].cWinned := 0;
      FPlayers[newIdx].cFailed := 0;
      FPlayers[newIdx].cScores := 0;
      FPlayers[newIdx].cTotal := 0;
      RefreshTable;
      mtPlayers.Last;
    end;
  finally
    dbgPlayers.SetFocus;
  end;
end;

procedure TFPlayers.btnAddRobotClick(Sender: TObject);
begin
  AddPlayer(Sender = btnAddRobot);
end;

procedure TFPlayers.btnCancelClick(Sender: TObject);
begin
  Close;
end;

procedure TFPlayers.btnDeleteClick(Sender: TObject);
begin
  DelPlayer;
end;

procedure TFPlayers.btnEditClick(Sender: TObject);
begin
  EditPlayer;
end;

procedure TFPlayers.btnResetAllStatClick(Sender: TObject);
begin
  if (Application.MessageBox('Сбросить всю статистику игроков?', 'Подтверждение', MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;
  ResetAllStatistic;
end;

procedure TFPlayers.btnResetStatisticClick(Sender: TObject);
begin
  if (not mtPlayers.Active) or mtPlayers.IsEmpty then exit;
  if (Application.MessageBox(pchar('Сбросить статистику игрока "' + mtPlayersNAME.AsString + '"?'), 'Подтверждение',
    MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;

  ResetStatistic;
end;

procedure TFPlayers.btnSaveClick(Sender: TObject);
begin
  r_ok := true;
  Close;
end;

function TFPlayers.CheckName(var AName: string): boolean;
var
  i: integer;

begin
  result := true;
  AName := Trim(Copy(AName, 1, 255));
  if AName = '' then
  begin
    result := false;
    exit;
  end;

  for i := 0 to Length(Players) - 1 do
    if AnsiLowerCase(AName) = AnsiLowerCase(Players[i].Name) then
    begin
      result := false;
      break;
    end;
end;

procedure TFPlayers.dbgPlayersGetCellParams(Sender: TObject; Column: TColumnEh; AFont: TFont; var Background: TColor; State: TGridDrawState);
begin
  if mtPlayersROBOT.AsInteger = 1 then AFont.Color := RGB(100, 100, 100)
  else AFont.Color := clNavy;
end;

procedure TFPlayers.DelPlayer;
var
  QPass: TFQueryPass;
  Idx: integer;
  s: string;
  i: integer;

begin
  QPass := TFQueryPass.Create(self);
  try
    if (not mtPlayers.Active) or mtPlayers.IsEmpty then exit;
    Idx := GetPlayerIndex(mtPlayersNAME.AsString);
    if (idx < 0) or (idx >= Length(FPlayers)) then exit;

    if (Application.MessageBox(pchar('Удалить игрока "' + FPlayers[Idx].Name + '"???'), 'Подтверждение',
      MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;

    if (FPlayers[Idx].Control in [ctHumanLocal, ctHumanRemote]) and (FPlayers[Idx].Password <> '') then
    begin
      if QPass.QueryPass(FPlayers[Idx].Name, s) then
      begin
        if s <> FPlayers[Idx].Password then
        begin
          Application.MessageBox(pchar('Неверный пароль'), 'Ошибка', MB_OK + MB_ICONERROR);
          exit;
        end;
      end else exit;
    end;

    // сначала удалить файл морды (из наборов не удаляем)
    {if FileExists(FSettings.DataDir + USER_DATA_DIR + FPlayers[Idx].FaceFile) and
      (not IniKeyExists(FSettings.DataDir + RES_CONFIG_FILE, RCFG_SEC_FACE, FPlayers[Idx].FaceFile, 1)) then
      DeleteFile(FSettings.DataDir + USER_DATA_DIR + FPlayers[Idx].FaceFile);}

    // удалим сохранения игры
    if FileExists(FSettings.DataDir + Format(SAVE_FILE, [FPlayers[Idx].Id])) then
      DeleteFile(FSettings.DataDir + Format(SAVE_FILE, [FPlayers[Idx].Id]));

    if Idx < Length(FPlayers) - 1 then
      for i := Idx + 1 to Length(FPlayers) - 1 do FPlayers[i-1] := FPlayers[i];

    SetLength(FPlayers, Length(FPlayers) - 1);
    RefreshTable;
    mtPlayers.Locate('NAME', FPlayers[Idx].Name, []);
  finally
    QPass.Free;
    dbgPlayers.SetFocus;
  end;
end;

procedure TFPlayers.EditPlayer;
var
  QPass: TFQueryPass;
  FEditRobot: TFRobotParams;
  FEditHuman: TFHumanParams;
  s{, newFn, err}: string;
  Idx: integer;
  c: boolean;

begin
  QPass := TFQueryPass.Create(self);
  try
    if (not mtPlayers.Active) or mtPlayers.IsEmpty then exit;
    Idx := GetPlayerIndex(mtPlayersNAME.AsString);
    if (idx < 0) or (idx >= Length(FPlayers)) then exit;

    c := false;
    if FPlayers[Idx].Control = ctRobot then
    begin
      FEditRobot := TFRobotParams.Create(self);
      FEditRobot.edName.Text := FPlayers[Idx].Name;
      FEditRobot.cbDifficulty.ItemIndex := Ord(FPlayers[Idx].Difficulty);
      FEditRobot.cbBehavior.ItemIndex := Ord(FPlayers[Idx].Behavior);
      FEditRobot.cbPlayStyle.ItemIndex := Ord(FPlayers[Idx].PlayStyle);
      FEditRobot.FaceFile := FPlayers[Idx].FaceFile;
      if FileExists(FSettings.DataDir + USER_DATA_DIR + FEditRobot.FaceFile) then
        try
          FEditRobot.imFace.Picture.LoadFromFile(FSettings.DataDir + USER_DATA_DIR + FEditRobot.FaceFile);
        except
        end;

      if FEditRobot.ShowModal = mrOk then
      begin
        s := Trim(Copy(FEditRobot.edName.Text, 1, 255));
        if s = '' then
        begin
          Application.MessageBox(pchar('Имя игрока пустое!'), 'Ошибка', MB_OK + MB_ICONERROR);
          exit;
        end;

        FPlayers[Idx].Name := s;
        if FEditRobot.FaceFileChanged then
        {begin
          if FileExists(FEditRobot.FaceFile) then
          begin
            newFn := FSettings.DataDir + USER_DATA_DIR + ExtractFileName(FEditRobot.FaceFile);
            if AnsiLowerCase(newFn) <> AnsiLowerCase(FEditRobot.FaceFile) then
              if not CopyFile(FEditRobot.FaceFile, newFn, err) then
                Application.MessageBox(pchar('Не удалось перенести файл с изображением в папку данных игры. ' +
                  'Изображение не изменено! Ошибка'#13#10 + err), 'Ошибка', MB_OK + MB_ICONERROR); }

            FPlayers[Idx].FaceFile := FEditRobot.FaceFile; //ExtractFileName(newFn);
          {end else
            FPlayers[Idx].FaceFile := '';
        end;}
        FPlayers[Idx].Password := '';
        FPlayers[Idx].Difficulty := TDifficulty(FEditRobot.cbDifficulty.ItemIndex);
        FPlayers[Idx].Behavior := TPlayerBehavior(FEditRobot.cbBehavior.ItemIndex);
        FPlayers[Idx].PlayStyle := TPlayerPlayStyle(FEditRobot.cbPlayStyle.ItemIndex);
        c := true;
      end;
    end else
    begin
      if FPlayers[Idx].Password <> '' then
      begin
        if QPass.QueryPass(FPlayers[Idx].Name, s) then
        begin
          if s <> FPlayers[Idx].Password then
          begin
            Application.MessageBox(pchar('Неверный пароль'), 'Ошибка', MB_OK + MB_ICONERROR);
            exit;
          end;
        end else exit;
      end;

      FEditHuman := TFHumanParams.Create(self);
      FEditHuman.edName.Text := FPlayers[Idx].Name;
      FEditHuman.edPassword.Text := FPlayers[Idx].Password;
      FEditHuman.edConfirmPass.Text := FPlayers[Idx].Password;
      FEditHuman.FaceFile := FPlayers[Idx].FaceFile;
      if FileExists(FSettings.DataDir + USER_DATA_DIR + FEditHuman.FaceFile) then
        try
          FEditHuman.imFace.Picture.LoadFromFile(FSettings.DataDir + USER_DATA_DIR + FEditHuman.FaceFile);
        except
        end;

      if FEditHuman.ShowModal = mrOk then
      begin
        s := Trim(Copy(FEditHuman.edName.Text, 1, 255));
        if s = '' then
        begin
          Application.MessageBox(pchar('Имя игрока пустое!'), 'Ошибка', MB_OK + MB_ICONERROR);
          exit;
        end;

        FPlayers[Idx].Name := s;
        if FEditHuman.FaceFileChanged then
        {begin
          if FileExists(FEditHuman.FaceFile) then
          begin
            newFn := FSettings.DataDir + USER_DATA_DIR + ExtractFileName(FEditHuman.FaceFile);
            if AnsiLowerCase(newFn) <> AnsiLowerCase(FEditHuman.FaceFile) then
              if not CopyFile(FEditHuman.FaceFile, newFn, err) then
                Application.MessageBox(pchar('Не удалось перенести файл с изображением в папку данных игры. ' +
                  'Изображение не изменено! Ошибка'#13#10 + err), 'Ошибка', MB_OK + MB_ICONERROR); }

            FPlayers[Idx].FaceFile := FEditHuman.FaceFile; //ExtractFileName(newFn);
          {end else
            FPlayers[Idx].FaceFile := '';
        end; }
        FPlayers[Idx].Password := Trim(FEditHuman.edPassword.Text);
        FPlayers[Idx].Difficulty := dfUndefined;
        c := true;
      end;
    end;

    if c then
    begin
      s := mtPlayersNAME.AsString;
      RefreshTable;
      mtPlayers.Locate('NAME', s, []);
    end;
  finally
    QPass.Free;
    dbgPlayers.SetFocus;
  end;
end;

procedure TFPlayers.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  if r_ok then ModalResult := mrOk;
end;

procedure TFPlayers.FormCreate(Sender: TObject);
begin
  r_ok := false;
end;

function TFPlayers.GetPlayerIndex(Name: string): integer;
var
  i: integer;

begin
  result := -1;

  for i := 0 to Length(FPlayers) - 1 do
    if FPlayers[i].Name = Name then
    begin
      result := i;
      break;
    end;
end;

procedure TFPlayers.mtPlayersCalcFields(DataSet: TDataSet);
begin
  if mtPlayersALL.AsInteger = 0 then
    mtPlayersAVG.AsFloat := mtPlayersSCORES.AsInteger
  else
    mtPlayersAVG.AsFloat := mtPlayersSCORES.AsInteger / mtPlayersALL.AsInteger;
end;

procedure TFPlayers.RefreshTable;
var
  i: integer;

begin
  mtPlayers.Close;
  mtPlayers.CreateDataSet;
  mtPlayers.EmptyTable;

  for i := 0 to Length(FPlayers) - 1 do
  begin
    mtPlayers.Append;
    mtPlayersID.AsString := FPlayers[i].Id;
    mtPlayersNAME.AsString := FPlayers[i].Name;
    mtPlayersROBOT.AsInteger := iif(FPlayers[i].Control = ctRobot, 1, 0);
    mtPlayersDIFFICULTY.AsInteger := iif(FPlayers[i].Control = ctRobot, Ord(FPlayers[i].Difficulty), Ord(dfUndefined));
    mtPlayersALL.AsInteger := FPlayers[i].cAll;
    mtPlayersCOMPLETED.AsInteger := FPlayers[i].cCompleted;
    mtPlayersINTERRUPTED.AsInteger := FPlayers[i].cInterrupted;
    mtPlayersWINNED.AsInteger := FPlayers[i].cWinned;
    mtPlayersFAILED.AsInteger := FPlayers[i].cFailed;
    mtPlayersSCORES.AsInteger := FPlayers[i].cScores;
    mtPlayersTOTAL.AsInteger := FPlayers[i].cTotal;
    mtPlayers.Post;
  end;
  mtPlayers.SortByFields('AVG DESC');
  mtPlayers.First;
end;

procedure TFPlayers.ResetAllStatistic;
var
  i: integer;
  s: string;

begin
  s := mtPlayersNAME.AsString;
  for i := 0 to Length(FPlayers) - 1 do ResetStatistic(i);
  RefreshTable;
  mtPlayers.Locate('NAME', s, []);
  dbgPlayers.SetFocus;
end;

procedure TFPlayers.ResetStatistic(PIndex: integer = -1);
var
  QPass: TFQueryPass;
  s: string;

begin
  QPass := TFQueryPass.Create(self);
  try
    if (not mtPlayers.Active) or mtPlayers.IsEmpty then exit;
    if PIndex < 0 then PIndex := GetPlayerIndex(mtPlayersNAME.AsString);
    if (PIndex < 0) or (PIndex >= Length(FPlayers)) then exit;

    if FPlayers[PIndex].Control in [ctHumanLocal, ctHumanRemote] then
      if FPlayers[PIndex].Password <> '' then
      begin
        if QPass.QueryPass(FPlayers[PIndex].Name, s) then
        begin
          if s <> FPlayers[PIndex].Password then
          begin
            Application.MessageBox(pchar('Неверный пароль'), 'Ошибка', MB_OK + MB_ICONERROR);
            exit;
          end;
        end else exit;
      end;

    FPlayers[PIndex].cAll := 0;
    FPlayers[PIndex].cCompleted := 0;
    FPlayers[PIndex].cInterrupted := 0;
    FPlayers[PIndex].cWinned := 0;
    FPlayers[PIndex].cFailed := 0;
    FPlayers[PIndex].cScores := 0;
    FPlayers[PIndex].cTotal := 0;

    s := mtPlayersNAME.AsString;
    RefreshTable;
    mtPlayers.Locate('NAME', s, []);
  finally
    QPass.Free;
    dbgPlayers.SetFocus;
  end;
end;

procedure TFPlayers.SetPlayers(Value: TPlayerList);
begin
  FPlayers := Value;
  RefreshTable;
end;

end.
