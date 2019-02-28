unit selPlayer;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, DBGridEh, StdCtrls, Buttons, Mask, DBCtrlsEh, DBLookupEh, MemTableDataEh, Db, MemTableEh,
  settings, utils, querypass, engine, ExtCtrls;

type
  TFSelPlayer = class(TForm)
    Label3: TLabel;
    cbPlayer: TDBLookupComboboxEh;
    btnStart: TBitBtn;
    btnCancel: TBitBtn;
    mtHumans: TMemTableEh;
    mtHumansNAME: TStringField;
    mtHumansALL: TIntegerField;
    mtHumansCOMPLETED: TIntegerField;
    mtHumansINTERRUPTED: TIntegerField;
    mtHumansWINNED: TIntegerField;
    mtHumansFAILED: TIntegerField;
    mtHumansSCORES: TIntegerField;
    mtHumansPASSWORD: TStringField;
    dsoHumans: TDataSource;
    mtHumansID: TStringField;
    chbNetwork: TCheckBox;
    GroupBox1: TGroupBox;
    rbnServer: TRadioButton;
    rbnClient: TRadioButton;
    Label1: TLabel;
    edServerIp: TEdit;
    mtHumansTOTAL: TIntegerField;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure btnCancelClick(Sender: TObject);
    procedure btnStartClick(Sender: TObject);
    procedure chbNetworkClick(Sender: TObject);
    procedure rbnClientClick(Sender: TObject);
  private
    r_ok: boolean;
  public
    function Execute(Players: TPlayerList; var PlayerId: string): boolean;
  end;

implementation

{$R *.dfm}

procedure TFSelPlayer.btnCancelClick(Sender: TObject);
begin
  Close;
end;

procedure TFSelPlayer.btnStartClick(Sender: TObject);
begin
  if VarIsNull(cbPlayer.KeyValue) then
  begin
    Application.MessageBox('Не выбран игрок!', 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  if chbNetwork.Checked and (not rbnServer.Checked) and (not rbnClient.Checked) then
  begin
    Application.MessageBox('Не указан тип сетевой игры!', 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  r_ok := true;
  Close;
end;

procedure TFSelPlayer.chbNetworkClick(Sender: TObject);
begin
  rbnServer.Enabled := chbNetwork.Checked;
  rbnClient.Enabled := chbNetwork.Checked;
  rbnClientClick(rbnClient);
end;

function TFSelPlayer.Execute(Players: TPlayerList; var PlayerId: string): boolean;
var
  i, idx: integer;
  s: string;
  QPass: TFQueryPass;

begin
  r_ok := false;
  result := false;
  QPass := TFQueryPass.Create(self);

  chbNetworkClick(chbNetwork);
  edServerIp.Text := FSettings.ServerIp;
  try
    mtHumans.Close;
    mtHumans.CreateDataSet;
    mtHumans.EmptyTable;

    for i := 0 to Length(Players) - 1 do
    begin
      if Players[i].Control = ctHumanLocal then
      begin
        mtHumans.Append;
        mtHumansID.AsString := Players[i].Id;
        mtHumansNAME.AsString := Players[i].Name;
        mtHumansPASSWORD.AsString := Players[i].Password;
        mtHumansALL.AsInteger := Players[i].cAll;
        mtHumansCOMPLETED.AsInteger := Players[i].cCompleted;
        mtHumansINTERRUPTED.AsInteger := Players[i].cInterrupted;
        mtHumansWINNED.AsInteger := Players[i].cWinned;
        mtHumansFAILED.AsInteger := Players[i].cFailed;
        mtHumansSCORES.AsInteger := Players[i].cScores;
        mtHumansTOTAL.AsInteger := Players[i].cTotal;
        mtHumans.Post;
      end;
    end;

    if mtHumans.IsEmpty then
    begin
      Application.MessageBox('В списке игроков нет ни одного локального игрока-человека!', 'Ошибка', MB_OK + MB_ICONERROR);
      exit;
    end;

    if mtHumans.Locate('ID', FSettings.LastPlayer, []) then cbPlayer.KeyValue := FSettings.LastPlayer;

    ShowModal;
    result := r_ok;
    if result then
    begin
      PlayerId := cbPlayer.KeyValue;
      idx := FindPlayerById(PlayerId, Players);
      if idx < 0 then exit;
      if Players[idx].Password <> '' then
      begin
        if QPass.QueryPass(Players[idx].Name, s) then
        begin
          if s <> Players[idx].Password then
          begin
            Application.MessageBox('Неверный пароль', 'Ошибка', MB_OK + MB_ICONERROR);
            result := false;
            exit;
          end;
        end else
        begin
          result := false;
          exit;
        end;
      end;

      FSettings.LastPlayer := PlayerId;
      FSettings.ServerIp := edServerIp.Text;
    end;
  finally
    QPass.Free;
  end;
end;

procedure TFSelPlayer.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  if r_ok then ModalResult := mrOk;
end;

procedure TFSelPlayer.rbnClientClick(Sender: TObject);
begin
  edServerIp.Enabled := chbNetwork.Checked and rbnClient.Checked;
  label1.Enabled := edServerIp.Enabled;
end;

end.
