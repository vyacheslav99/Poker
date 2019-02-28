unit querypass;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  StdCtrls, Buttons;

type
  TFQueryPass = class(TForm)
    GroupBox1: TGroupBox;
    btnOk: TBitBtn;
    btnCancel: TBitBtn;
    Label3: TLabel;
    edPass: TEdit;
    Label1: TLabel;
  private
  public
    function QueryPass(APlayer: string; var APass: string): boolean;
  end;

implementation

{$R *.dfm}

{ TFQueryPass }

function TFQueryPass.QueryPass(APlayer: string; var APass: string): boolean;
begin
  Label1.Caption := 'Игрок "' + APlayer + '" защищен паролем. Для продолжения введите пароль.';
  result := Self.ShowModal = mrOk;
  if result then APass := Trim(edPass.Text)
  else APass := '';
end;

end.
