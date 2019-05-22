program poker;

uses
  Forms,
  SysUtils,
  Windows,
  Classes,
  main in 'src\main.pas' {FMain},
  utils in 'src\utils.pas',
  settings in 'src\settings.pas' {FSettings},
  players in 'src\players.pas' {FPlayers},
  humanParams in 'src\humanParams.pas' {FHumanParams},
  robotParams in 'src\robotParams.pas' {FRobotParams},
  start in 'src\start.pas' {FStartDialog},
  selPlayer in 'src\selPlayer.pas' {FSelPlayer},
  querypass in 'src\querypass.pas' {FQueryPass},
  engine in 'src\engine.pas',
  wjoker in 'src\wjoker.pas' {FWalkJoker},
  msg_box in 'src\msg_box.pas' {FGameMsg},
  load in 'src\load.pas' {FLoad},
  selimage in 'src\selimage.pas' {FSelImage},
  imgUtils in 'src\imgUtils.pas',
  gchart in 'src\gchart.pas' {FGameChart},
  network in 'src\network.pas' {dmNetwork: TDataModule},
  example in 'src\example.pas' {frmExample: TFrame},
  engine_net in 'src\engine_net.pas';

{$R *.res}

var
  e: string;
  fl: TFLoad;
  
begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;
  Application.Title := 'Расписной покер';

  fl := TFLoad.Create(Application);
  try
    fl.Show;
    fl.lbProgress.Caption := 'Checking cache...';
    Application.ProcessMessages;

    if not LoadResources(ExtractFilePath(Application.ExeName) + DATA_DIR + RES_FILE,
      ExtractFilePath(Application.ExeName) + DATA_DIR + RES_DIR, false, fl, e) then
    begin
      Application.MessageBox(pchar('Ошибка загрузки ресурсов! ' + e), 'Расписной покер', MB_OK + MB_ICONERROR);
      exit;
    end;

    fl.lbProgress.Caption := 'Preparing UserData...';
    Application.ProcessMessages;
    if not MoveDir(ExtractFilePath(Application.ExeName) + DATA_DIR + FACE_DIR,
      ExtractFilePath(Application.ExeName) + DATA_DIR + USER_DATA_DIR, false, false, fl, e) then
      Application.MessageBox(pchar('Ошибка загузки картинок игроков! ' + e), 'Расписной покер', MB_OK + MB_ICONERROR);
  finally
    fl.Free;
  end;
  
  Application.CreateForm(TFMain, FMain);
  //if (ParamCount >= 1) and (ParamStr(1) = 'debug') then FMain.DbgMode := true;
  Application.Run;
end.
