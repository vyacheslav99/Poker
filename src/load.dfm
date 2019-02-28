object FLoad: TFLoad
  Left = 0
  Top = 0
  BorderStyle = bsNone
  Caption = 'FLoad'
  ClientHeight = 50
  ClientWidth = 250
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poScreenCenter
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 250
    Height = 50
    Align = alClient
    TabOrder = 0
    object lbProgress: TLabel
      Left = 8
      Top = 10
      Width = 234
      Height = 13
      Alignment = taCenter
      AutoSize = False
      Caption = #1056#1072#1089#1087#1072#1082#1086#1074#1082#1072' '#1088#1077#1089#1091#1088#1089#1086#1074': 99%'
    end
    object lbFile: TLabel
      Left = 8
      Top = 27
      Width = 234
      Height = 13
      Alignment = taCenter
      AutoSize = False
      Caption = 'bg1.bmp'
    end
  end
end
