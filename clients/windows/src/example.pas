unit example;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms, 
  Dialogs, StdCtrls, JvBackgrounds;

type
  TfrmExample = class(TFrame)
    bgImageExample: TJvBackground;
    lbExample: TLabel;
  private
    { Private declarations }
  public
    { Public declarations }
  end;

implementation

{$R *.dfm}

end.
