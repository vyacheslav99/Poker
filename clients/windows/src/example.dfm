object frmExample: TfrmExample
  Left = 0
  Top = 0
  Width = 296
  Height = 182
  TabOrder = 0
  object lbExample: TLabel
    Left = 5
    Top = 3
    Width = 48
    Height = 13
    Caption = 'lbExample'
    ParentShowHint = False
    ShowHint = True
  end
  object bgImageExample: TJvBackground
    Image.Mode = bmTopLeft
    Image.TileWidth = 115
    Image.TileHeight = 74
    Clients.Clients = (
      'frmExample')
    Left = 93
    Top = 8
  end
end
