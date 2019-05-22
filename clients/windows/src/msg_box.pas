unit msg_box;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Buttons, ExtCtrls;

type
  TFGameMsg = class(TForm)
    btnCancel: TBitBtn;
    btnSave: TBitBtn;
    lbMessage: TLabel;
    chbNoShow: TCheckBox;
    tmrAutoHide: TTimer;
    procedure tmrAutoHideTimer(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

implementation

{$R *.dfm}

procedure TFGameMsg.tmrAutoHideTimer(Sender: TObject);
begin
  Close;
end;

end.
