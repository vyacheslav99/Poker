unit gchart;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, TeEngine, Series, ExtCtrls, TeeProcs, Chart, DBChart, StdCtrls;

type
  TFGameChart = class(TForm)
    DBChart: TDBChart;
    Series1: TLineSeries;
    Series2: TLineSeries;
    Series3: TLineSeries;
    Panel1: TPanel;
    chbShowMarks: TCheckBox;
    procedure chbShowMarksClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

implementation

{$R *.dfm}

uses main, settings;

procedure TFGameChart.chbShowMarksClick(Sender: TObject);
var
  i: integer;

begin
  for i := 0 to DBChart.SeriesCount - 1 do
    DBChart.Series[i].Marks.Visible := chbShowMarks.Checked;
end;

procedure TFGameChart.FormCreate(Sender: TObject);
begin
  chbShowMarks.Checked := FSettings.ChartMarksVisible;
  chbShowMarksClick(chbShowMarks);
end;

procedure TFGameChart.FormDestroy(Sender: TObject);
begin
  FSettings.ChartMarksVisible := chbShowMarks.Checked;
end;

end.
