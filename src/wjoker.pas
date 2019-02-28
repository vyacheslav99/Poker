unit wjoker;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Buttons, ExtCtrls;

type
  TFWalkJoker = class(TForm)
    btnOk: TBitBtn;
    btnCancel: TBitBtn;
    GroupBox1: TGroupBox;
    cbJokerAction: TComboBox;
    lbSelectLear: TLabel;
    Bevel1: TBevel;
    cbLear: TComboBox;
    lbSelectCard: TLabel;
    cbCard: TComboBox;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure btnOkClick(Sender: TObject);
    procedure btnCancelClick(Sender: TObject);
    procedure cbJokerActionChange(Sender: TObject);
    procedure FormShow(Sender: TObject);
  private
    r_ok: boolean;
  public
    { Public declarations }
  end;

implementation

{$R *.dfm}

procedure TFWalkJoker.btnCancelClick(Sender: TObject);
begin
  Close;
end;

procedure TFWalkJoker.btnOkClick(Sender: TObject);
begin
  r_ok := true;
  Close;
end;

procedure TFWalkJoker.cbJokerActionChange(Sender: TObject);
begin
  cbLear.ItemIndex := -1;
  cbLear.Enabled := false;
  lbSelectLear.Enabled := false;

  cbCard.ItemIndex := -1;
  cbCard.Enabled := false;
  lbSelectCard.Enabled := false;

  case cbJokerAction.ItemIndex of
    0: ;
    1:
    begin
      cbLear.ItemIndex := 0;
      cbLear.Enabled := true;
      lbSelectLear.Enabled := true;

      cbCard.ItemIndex := 0;
      cbCard.Enabled := true;
      lbSelectCard.Enabled := true;
    end;
    2, 3:
    begin
      if cbJokerAction.Text = 'Скинуть' then exit;
      cbLear.ItemIndex := 0;
      cbLear.Enabled := true;
      lbSelectLear.Enabled := true;
    end;
  end;
end;

procedure TFWalkJoker.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  if r_ok then ModalResult := mrOk;
  Action := caHide;
end;

procedure TFWalkJoker.FormShow(Sender: TObject);
begin
  r_ok := false;
  cbJokerAction.ItemIndex := 0;
  cbJokerActionChange(cbJokerAction);
end;

end.
