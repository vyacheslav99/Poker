unit imgUtils;

interface

uses
  Windows, Classes, SysUtils, Graphics, Math, jpeg, GifImage;

const
  HLSMAX = 240;
  RGBMAX = 255;
  UNDEFINED = (HLSMAX * 2) div 3;

type
  THLSColor = record
    {H - оттенок, L - яркость, S - насыщенность}
    H, L, S: integer;
  end;

  TRGB = record
    R, G, B: Byte;
  end;
  pRGB = ^TRGB;

  TIMGType = (itBitmap, itJpeg, itIcon, itGif, itPng, itXpm);

  TIconHeader = record
    reserved: word;
    _type: word;
    count: word;
  end;

  TIconHeaderCat = record
    width: byte;
    height: byte;
    colors: byte;
    reserved: byte;
    planes: word;
    bpp: word;
    size: integer;
    offset: integer;
  end;

function HueToRGB(n1, n2, hue: single): single;
procedure RGBtoHLS(R, G, B: byte; var H, L, S: integer); overload;
function RGBtoHLS(Color: TColor): THLSColor; overload;
procedure HLStoRGB(H, L, S: integer; var R, G, B: integer); overload;
function HLStoRGB(HLSColor: THLSColor): TColor; overload;
function LoadPicture(PicFile: string): TBitmap;
function DefineImgType(FileExt: string): TIMGType;
procedure DecreaseBitmap(bm: TBitmap; nw, nh: Integer);
procedure IncreaseBitmap(var bm: TBitMap; dx, dy: single);
procedure InvertBitmap(bm: TBitmap);
function InvertColor(Color: TColor; WhiteCenter: boolean = true): TColor;
function InvertBright(Color: TColor): TColor;
procedure ChangeGamma(bm: TBitmap; L: Double; pxFormat: TPixelFormat);

implementation

function HueToRGB(n1, n2, hue: single): single;
begin
  if (hue < 0) then hue := hue + HLSMAX;
  if (hue > HLSMAX) then hue := hue - HLSMAX;
  if (hue < (HLSMAX / 6)) then result := (n1 + (((n2 - n1) * hue + (HLSMAX / 12)) / (HLSMAX / 6)))
  else if (hue < (HLSMAX / 2)) then result := n2
  else if (hue < ((HLSMAX * 2) / 3)) then
    result := (n1 + (((n2 - n1) * (((HLSMAX * 2) / 3) - hue) + (HLSMAX / 12)) / (HLSMAX / 6)))
  else result := (n1);
end;

procedure RGBtoHLS(R, G, B: byte; var H, L, S: integer);
var
  cMax, cMin: integer;
  Rdelta, Gdelta, Bdelta: single;

begin
  {H - оттенок, L - яркость, S - насыщенность}
  {R - красный, G - зеленый, B - голубой}

  cMax := max(max(R, G), B);
  cMin := min(min(R, G), B);
  L := round((((cMax + cMin) * HLSMAX) + RGBMAX) / (2 * RGBMAX));

  if (cMax = cMin) then
  begin
    S := 0;
    H := UNDEFINED;
  end else
  begin
    if (L <= (HLSMAX / 2)) then
      S := round((((cMax - cMin) * HLSMAX) + ((cMax + cMin) / 2)) / (cMax + cMin))
    else
      S := round((((cMax - cMin) * HLSMAX) + ((2 * RGBMAX - cMax - cMin) / 2)) / (2 * RGBMAX - cMax - cMin));

    Rdelta := (((cMax - R) * (HLSMAX / 6)) + ((cMax - cMin) / 2)) / (cMax - cMin);
    Gdelta := (((cMax - G) * (HLSMAX / 6)) + ((cMax - cMin) / 2)) / (cMax - cMin);
    Bdelta := (((cMax - B) * (HLSMAX / 6)) + ((cMax - cMin) / 2)) / (cMax - cMin);
    if (R = cMax) then
      H := round(Bdelta - Gdelta)
    else
      if (G = cMax) then
        H := round((HLSMAX / 3) + Rdelta - Bdelta)
      else
        H := round(((2 * HLSMAX) / 3) + Gdelta - Rdelta);

    if (H < 0) then H := H + HLSMAX;
    if (H > HLSMAX) then H := H - HLSMAX;
  end;

  if S < 0 then S := 0;
  if S > HLSMAX then S := HLSMAX;
  if L < 0 then L := 0;
  if L > HLSMAX then L := HLSMAX;
end;

function RGBtoHLS(Color: TColor): THLSColor;
begin
  RGBtoHLS(GetRValue(Color), GetGValue(Color), GetBValue(Color), result.H, result.L, result.S);
end;

procedure HLStoRGB(H, L, S: integer; var R, G, B: integer);
var
  Magic1, Magic2: single;

begin
  if (S = 0) then
  begin
    B := round((L * RGBMAX) / HLSMAX);
    R := B;
    G := B;
  end else
  begin
    if (L <= (HLSMAX / 2)) then
      Magic2 := (L * (HLSMAX + S) + (HLSMAX / 2)) / HLSMAX
    else
      Magic2 := L + S - ((L * S) + (HLSMAX / 2)) / HLSMAX;
    Magic1 := 2 * L - Magic2;
    R := round((HueToRGB(Magic1, Magic2, H + (HLSMAX / 3)) * RGBMAX + (HLSMAX / 2)) / HLSMAX);
    G := round((HueToRGB(Magic1, Magic2, H) * RGBMAX + (HLSMAX / 2)) / HLSMAX);
    B := round((HueToRGB(Magic1, Magic2, H - (HLSMAX / 3)) * RGBMAX + (HLSMAX / 2)) / HLSMAX);
  end;

  if R < 0 then R := 0;
  if R > RGBMAX then R := RGBMAX;
  if G < 0 then G := 0;
  if G > RGBMAX then G := RGBMAX;
  if B < 0 then B := 0;
  if B > RGBMAX then B := RGBMAX;
end;

function HLStoRGB(HLSColor: THLSColor): TColor;
var
  r, g, b: integer;

begin
  HLStoRGB(HLSColor.H, HLSColor.L, HLSColor.S, r, g, b);
  result := RGB(r, g, b);
end;

function LoadPicture(PicFile: string): TBitmap;
var
  jpg: TJPEGImage;
  ico: TIcon;
  pic: TPicture;
  picType: TIMGType;
  gif: TGIFImage;
  ih: TIconHeader;
  icat: TIconHeaderCat;
  fs: TFileStream;
  i: integer;
  w, h: byte;

begin
  result := TBitmap.Create;
  picType := DefineImgType(ExtractFileExt(PicFile));
  case picType of
    itBitmap: result.LoadFromFile(PicFile);
    itJpeg:
    begin
      jpg := TJPEGImage.Create;
      jpg.LoadFromFile(PicFile);
      result.Assign(jpg);
      jpg.Free;
    end;
    itIcon:
    begin
      w := 0;
      h := 0;
      //зачитываем заголовок иконки, определяем размер самого большого из изображений
      //почему-то ico.Height и ico.Width показывают всегда 32x32, при любом реальном размере изображения
      //кроме того, если изображений неск., ico.LoadFromFile() загружает то, к-рое ближе всего
      //по размерам к уже выставленному у ico размеру, поэтому перед загрузкой желательно
      //задать нужный размер
      fs := TFileStream.Create(PicFile, fmOpenRead);
      fs.Read(ih, 6);
      for i := 1 to ih.count do
      begin
        fs.Read(icat, 16);
        if (icat.width > w) and (icat.height > h) then
        begin
          w := icat.width;
          h := icat.height;
        end;
      end;
      fs.Free;
      ico := TIcon.Create;
      ico.SetSize(w, h);
      ico.LoadFromFile(PicFile);
      result.Height := h;//ico.Height;
      result.Width := w;//ico.Width;
      result.Canvas.Draw(0, 0, ico);
      ico.Free;
    end;
    itGif:
    begin
      gif := TGIFImage.Create;
      gif.LoadFromFile(PicFile);
      result.Assign(gif.Bitmap);
      gif.Free;
    end;
    itPng:
    begin
      pic := TPicture.Create;
      pic.LoadFromFile(PicFile);
      result.Height := pic.Graphic.Height;
      result.Width := pic.Graphic.Width;
      result.Canvas.Draw(0, 0, pic.Graphic);
      pic.Free;
    end;
{    itXpm:
    begin
      pic := TPicture.Create;
      pic.LoadFromFile(PicFile);
      bmp.Height := pic.Graphic.Height;
      bmp.Width := pic.Graphic.Width;
      bmp.Canvas.Draw(0, 0, pic.Graphic);
    end;}
  end;
end;

function DefineImgType(FileExt: string): TIMGType;
begin
  result := itBitmap;
  FileExt := AnsiLowerCase(FileExt);
  if FileExt = '' then exit;
  if FileExt[1] = '.' then Delete(FileExt, 1, 1);
  if (FileExt = 'jpg') or (FileExt = 'jpeg') then result := itJpeg
  else if (FileExt = 'bmp') then result := itBitmap
  else if (FileExt = 'ico') then result := itIcon
  else if (FileExt = 'gif') then result := itGif
  else if (FileExt = 'png') then result := itPng
  else if (FileExt = 'xpm') then result := itXpm;
end;

procedure DecreaseBitmap(bm: TBitmap; nw, nh: Integer);
var
  imgd: TBitmap;
  xini, xfi, yini, yfi, saltx, salty: single;
  x, y, px, py, tpix: integer;
  PixelColor: TColor;
  r, g, b: longint;

  function MyRound(const X: Double): Integer;
  begin
    Result := Trunc(x);
    if Frac(x) >= 0.5 then
      if x >= 0 then Result := Result + 1
      else Result := Result - 1;
   // Result := Trunc(X + (-2 * Ord(X < 0) + 1) * 0.5);
  end;

begin
  //пропорциональное изменение (в основном уменьшение) размера изображения
  imgd := TBitmap.Create;
  imgd.Width := nw;
  imgd.Height := nh;
  saltx := bm.Width / nw;
  salty := bm.Height / nh;
  yfi := 0;

  for y := 0 to nh - 1 do
  begin
    yini := yfi;
    yfi  := yini + salty;
    if yfi >= bm.Height then yfi := bm.Height - 1;
    xfi := 0;

    for x := 0 to nw - 1 do
    begin
      xini := xfi;
      xfi  := xini + saltx;
      if xfi >= bm.Width then xfi := bm.Width - 1;
      r := 0;
      g := 0;
      b := 0;
      tpix := 0;

      for py := MyRound(yini) to MyRound(yfi) do
      begin
        for px := MyRound(xini) to MyRound(xfi) do
        begin
          Inc(tpix);
          PixelColor := ColorToRGB(bm.Canvas.Pixels[px, py]);
          r := r + GetRValue(PixelColor);
          g := g + GetGValue(PixelColor);
          b := b + GetBValue(PixelColor);
        end;
      end;

      imgd.Canvas.Pixels[x, y] := rgb(MyRound(r / tpix), MyRound(g / tpix), MyRound(b / tpix));
    end;
  end;
  bm.Assign(imgd);
end;

procedure IncreaseBitmap(var bm: TBitMap; dx, dy: single);
var
  bm1: TBitMap;
  z1, z2: single;
  k, k1, k2: single;
  x1, y1: integer;
  c: array [0..1, 0..1, 0..2] of byte;
  res: array [0..2] of byte;
  x, y: integer;
  xp, yp: integer;
  xo, yo: integer;
  col: integer;
  pix: TColor;

begin
  //пропорциональное увеличение изображения
  bm1 := TBitMap.Create;
  bm1.Width := round(bm.Width * dx);
  bm1.Height := round(bm.Height * dy);

  for y := 0 to bm1.Height - 1 do
  begin
    for x := 0 to bm1.Width - 1 do
    begin
      xo := trunc(x / dx);
      yo := trunc(y / dy);
      x1 := round(xo * dx);
      y1 := round(yo * dy);

      for yp := 0 to 1 do
        for xp := 0 to 1 do
        begin
          pix := bm.Canvas.Pixels[xo + xp, yo + yp];
          c[xp, yp, 0] := GetRValue(pix);
          c[xp, yp, 1] := GetGValue(pix);
          c[xp, yp, 2] := GetBValue(pix);
        end;

      for col := 0 to 2 do
      begin
        k1 := (c[1,0,col] - c[0,0,col]) / dx;
        z1 := x * k1 + c[0,0,col] - x1 * k1;
        k2 := (c[1,1,col] - c[0,1,col]) / dx;
        z2 := x * k2 + c[0,1,col] - x1 * k2;
        k := (z2 - z1) / dy;
        res[col] := round(y * k + z1 - y1 * k);
      end;

      bm1.Canvas.Pixels[x,y] := RGB(res[0], res[1], res[2]);
    end;
  end;
  bm.Assign(bm1);
end;

procedure InvertBitmap(bm: TBitmap);
var
  x, y: Integer;
  BA: PByteArray;

begin
  bm.PixelFormat := pf24Bit;
  for y := 0 to bm.Height - 1 do
  begin
    BA := bm.ScanLine[y];
    for x := 0 to bm.Width * 3 - 1 do
      BA[x] := 255 - BA[x];
  end;
end;

function InvertColor(Color: TColor; WhiteCenter: boolean): TColor;
begin
  // получение негатива цвета
  if WhiteCenter and (((GetRValue(Color) >= 120) and (GetRValue(Color) <= 136)) and
    ((GetGValue(Color) >= 120) and (GetGValue(Color) <= 136)) and
    ((GetBValue(Color) >= 120) and (GetBValue(Color) <= 136))) then
    result := clWhite
  else
    result := RGB(255 - GetRValue(Color), 255 - GetGValue(Color), 255 - GetBValue(Color));
end;

function InvertBright(Color: TColor): TColor;
var
  hc: THLSColor;

begin
  // если яркость темнее средней яркости, возвращает белый, если светлее - черный
  hc := RGBtoHLS(Color);
  if hc.L < 120 then result := clWhite
  else result := clBlack;
end;

procedure ChangeGamma(bm: TBitmap; L: Double; pxFormat: TPixelFormat);
var
//  Dest: pRGB;
  X, Y: Word;
  GT: array[0..255] of Byte;
  c: TColor;

begin
  //в пределах -10<=L<=10 изменения имеют смысл, дальше увеличение(уменьшение) ничего не дает,
  //остается то же, что и при пороговом значениии
  bm.PixelFormat := pxFormat;
  GT[0] := 0;
  if L = 0 then L := 0.001;
  for X := 1 to 255 do
    GT[X] := Round(255 * Power(X / 255, 1 / L));

  for Y := 0 to bm.Height - 1 do
  begin
    //Dest := bm.ScanLine[y];
    for X := 0 to bm.Width - 1 do
    begin
      c := bm.Canvas.Pixels[X, Y];
      c := RGB(GT[GetRValue(c)], GT[GetGValue(c)], GT[GetBValue(c)]);
      bm.Canvas.Pixels[X, Y] := c;
     { with Dest^ do
      begin
        R := GT[R];
        G := GT[G];
        B := GT[B];
      end;
      Inc(Dest);}
    end;
  end;
end;

end.
