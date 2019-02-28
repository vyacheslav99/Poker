unit load;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ExtCtrls;

type
  TFLoad = class(TForm)
    Panel1: TPanel;
    lbProgress: TLabel;
    lbFile: TLabel;
    procedure FormShow(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

implementation

{$R *.dfm}

procedure TFLoad.FormShow(Sender: TObject);
begin
  lbProgress.Caption := '';
  lbFile.Caption := '';
  Application.ProcessMessages;
end;

end.
