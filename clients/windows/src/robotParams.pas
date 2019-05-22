unit robotParams;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ExtCtrls, StdCtrls, Buttons, utils, Menus, selimage;

type
  TFRobotParams = class(TForm)
    btnSave: TBitBtn;
    btnCancel: TBitBtn;
    GroupBox1: TGroupBox;
    Label1: TLabel;
    edName: TEdit;
    GroupBox2: TGroupBox;
    btnSelectFaceImage: TButton;
    imFace: TImage;
    OpenDialog: TOpenDialog;
    btnClearFaceImage: TButton;
    GroupBox3: TGroupBox;
    Label2: TLabel;
    cbBehavior: TComboBox;
    Label3: TLabel;
    cbPlayStyle: TComboBox;
    Label4: TLabel;
    cbDifficulty: TComboBox;
    pmSelImage: TPopupMenu;
    N1: TMenuItem;
    N2: TMenuItem; // Было так:   Полный ноль,Новичок,Опытный,Сильный,Профессионал,Шулер
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

procedure TFRobotParams.btnCancelClick(Sender: TObject);
begin
  Close;
end;

procedure TFRobotParams.btnClearFaceImageClick(Sender: TObject);
begin
  imFace.Picture.Assign(nil);
  FaceFile := '';
  FaceFileChanged := true;
end;

procedure TFRobotParams.btnSaveClick(Sender: TObject);
begin
  r_ok := true;
  Close;
end;

procedure TFRobotParams.btnSelectFaceImageClick(Sender: TObject);
{var
  m: TMouse;}

begin
  //pmSelImage.Popup(m.CursorPos.X, m.CursorPos.Y);
  SelectStdImage;
end;

procedure TFRobotParams.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  if r_ok then ModalResult := mrOk;
end;

procedure TFRobotParams.FormCreate(Sender: TObject);
begin
  r_ok := false;
  FaceFileChanged := false;
  FSelImg := TFSelImage.Create(self);
end;

procedure TFRobotParams.FormDestroy(Sender: TObject);
begin
  FSelImg.Free;
end;

procedure TFRobotParams.N1Click(Sender: TObject);
begin
  SelectStdImage;
end;

procedure TFRobotParams.N2Click(Sender: TObject);
begin
  //SelectUserImage;
end;

procedure TFRobotParams.SelectStdImage;
begin
  if FSelImg.ShowModal = mrOk then
  begin
    imFace.Picture.LoadFromFile(FSettings.DataDir + USER_DATA_DIR + FSelImg.Selected);
    FaceFile := {FSettings.DataDir + USER_DATA_DIR +} FSelImg.Selected;
    FaceFileChanged := true;
  end;
end;

{procedure TFRobotParams.SelectUserImage;
begin
  if OpenDialog.Execute then
  begin
    imFace.Picture.LoadFromFile(OpenDialog.FileName);
    FaceFile := OpenDialog.FileName;
    FaceFileChanged := true;
  end;
end; }

end.
