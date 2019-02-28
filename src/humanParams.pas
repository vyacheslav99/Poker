unit humanParams;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ExtCtrls, StdCtrls, Buttons, utils, Menus, selimage;

type
  TFHumanParams = class(TForm)
    btnSave: TBitBtn;
    btnCancel: TBitBtn;
    GroupBox1: TGroupBox;
    Label1: TLabel;
    edName: TEdit;
    GroupBox2: TGroupBox;
    btnSelectFaceImage: TButton;
    imFace: TImage;
    OpenDialog: TOpenDialog;
    Label2: TLabel;
    edPassword: TEdit;
    edConfirmPass: TEdit;
    Label3: TLabel;
    btnClearFaceImage: TButton;
    pmSelImage: TPopupMenu;
    N1: TMenuItem;
    N2: TMenuItem;
    procedure FormCreate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure btnSaveClick(Sender: TObject);
    procedure btnCancelClick(Sender: TObject);
    procedure btnSelectFaceImageClick(Sender: TObject);
    procedure btnClearFaceImageClick(Sender: TObject);
    procedure N1Click(Sender: TObject);
    procedure N2Click(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
  private
    r_ok: boolean;
    FSelImg: TFSelImage;
    procedure SelectStdImage;
    //procedure SelectUserImage;
  public
    FaceFile: string;
    FaceFileChanged: boolean;
  end;

implementation

{$R *.dfm}

uses settings;

procedure TFHumanParams.btnCancelClick(Sender: TObject);
begin
  Close;
end;

procedure TFHumanParams.btnClearFaceImageClick(Sender: TObject);
begin
  imFace.Picture.Assign(nil);
  FaceFile := '';
  FaceFileChanged := true;
end;

procedure TFHumanParams.btnSaveClick(Sender: TObject);
begin
  if (edPassword.Text <> edConfirmPass.Text) then
  begin
    Application.MessageBox('Пароль и повтор пароля не совпадают!', 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  r_ok := true;
  Close;
end;

procedure TFHumanParams.btnSelectFaceImageClick(Sender: TObject);
{var
  m: TMouse;}

begin
//  pmSelImage.Popup(m.CursorPos.X, m.CursorPos.Y);
  SelectStdImage;
end;

procedure TFHumanParams.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  if r_ok then ModalResult := mrOk;
end;

procedure TFHumanParams.FormCreate(Sender: TObject);
begin
  r_ok := false;
  FaceFileChanged := false;
  FSelImg := TFSelImage.Create(self);
end;

procedure TFHumanParams.FormDestroy(Sender: TObject);
begin
  FSelImg.Free;
end;

procedure TFHumanParams.N1Click(Sender: TObject);
begin
  SelectStdImage;
end;

procedure TFHumanParams.N2Click(Sender: TObject);
begin
 // SelectUserImage;
end;

procedure TFHumanParams.SelectStdImage;
begin
  if FSelImg.ShowModal = mrOk then
  begin
    imFace.Picture.LoadFromFile(FSettings.DataDir + USER_DATA_DIR + FSelImg.Selected);
    FaceFile := {FSettings.DataDir + USER_DATA_DIR +} FSelImg.Selected;
    FaceFileChanged := true;
  end;
end;

{procedure TFHumanParams.SelectUserImage;
begin
  if OpenDialog.Execute then
  begin
    imFace.Picture.LoadFromFile(OpenDialog.FileName);
    FaceFile := OpenDialog.FileName;
    FaceFileChanged := true;
  end;
end;}

end.
