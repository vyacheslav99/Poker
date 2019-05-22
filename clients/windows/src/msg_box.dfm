object FGameMsg: TFGameMsg
  Left = 0
  Top = 0
  BorderStyle = bsDialog
  Caption = 'FGameMsg'
  ClientHeight = 108
  ClientWidth = 359
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poMainFormCenter
  DesignSize = (
    359
    108)
  PixelsPerInch = 96
  TextHeight = 13
  object lbMessage: TLabel
    Left = 8
    Top = 8
    Width = 343
    Height = 36
    Alignment = taCenter
    Anchors = [akLeft, akTop, akRight, akBottom]
    AutoSize = False
    Caption = 'lbMessage'
    Layout = tlCenter
    WordWrap = True
    ExplicitHeight = 56
  end
  object btnCancel: TBitBtn
    Left = 268
    Top = 73
    Width = 83
    Height = 27
    Anchors = [akRight, akBottom]
    Cancel = True
    Caption = #1054#1090#1084#1077#1085#1072
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -11
    Font.Name = 'Tahoma'
    Font.Style = []
    ModalResult = 2
    ParentFont = False
    TabOrder = 0
    Glyph.Data = {
      36040000424D3604000000000000360000002800000010000000100000000100
      2000000000000004000000000000000000000000000000000000FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF000000B5001821BD000808B500FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF000808B5002129BD000000B500FF00FF00FF00FF00FF00FF00FF00FF000008
      C6003142D6008CADFF005A73E7000008BD00FF00FF00FF00FF00FF00FF000808
      BD005A73E7008CB5FF003142D6000008C600FF00FF00FF00FF00FF00FF002131
      D6007394FF007B9CFF007B9CFF005263EF000818CE00FF00FF000818CE00526B
      EF007B9CFF007B9CFF007B9CFF002931D600FF00FF00FF00FF00FF00FF001021
      DE00425AF700526BFF005263FF005A73FF00425AEF001021DE00425AEF00637B
      FF005263FF005A6BFF004A63F7001021DE00FF00FF00FF00FF00FF00FF00FF00
      FF001021E7003142F7003942FF003142FF003952FF00425AFF004252FF003139
      FF003942FF00314AF7001021E700FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF001829EF002131F7001821FF001818F7001821FF001818F7001821
      FF002131F7001829EF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF001831FF001829FF002121F7002129F7002129F7001821
      F7001831FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF001831FF003142FF004A5AFF005263FF005A6BFF005A6BFF005263
      FF00394AFF001831FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF001831FF00394AFF005263FF006373FF00637BFF006373FF006B7BFF00637B
      FF005A6BFF003952FF001831FF00FF00FF00FF00FF00FF00FF00FF00FF002131
      FF00394AFF005A63FF006373FF00738CFF00526BFF002139FF00526BFF007B94
      FF006B84FF006373FF004252FF002131FF00FF00FF00FF00FF00FF00FF002139
      FF00525AFF006373FF00738CFF00526BFF001831FF00FF00FF001831FF005A73
      FF008494FF007384FF005A6BFF002939FF00FF00FF00FF00FF00FF00FF001831
      FF00314AFF006B7BFF00526BFF001831FF00FF00FF00FF00FF00FF00FF001831
      FF005A73FF00738CFF00394AFF001831FF00FF00FF00FF00FF00FF00FF00FF00
      FF001831FF00314AFF002139FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF002139FF00314AFF001831FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00}
  end
  object btnSave: TBitBtn
    Left = 171
    Top = 73
    Width = 83
    Height = 27
    Anchors = [akRight, akBottom]
    Caption = #1054#1050
    Default = True
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -11
    Font.Name = 'Tahoma'
    Font.Style = []
    ModalResult = 1
    ParentFont = False
    TabOrder = 1
    Glyph.Data = {
      36040000424D3604000000000000360000002800000010000000100000000100
      2000000000000004000000000000000000000000000000000000FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF003194100052A539004A9C2900318C0800FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00319C210052A54200C6F7DE00B5EFC600429C21003194
      1000FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF0039A531004AAD4200ADEFCE009CFFEF009CFFE7009CE7AD00429C
      2100FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF0039AD4A004AB5520094EFB5008CFFD6007BFFCE007BFFC6008CFFCE0084DE
      9C00399C2100FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF0042BD
      5A004ABD5A0084E7A5007BF7BD007BF7BD007BEFB5007BF7BD007BF7B50084F7
      BD0073D68400399C2900FF00FF00FF00FF00FF00FF00FF00FF00FF00FF0042BD
      630063DE8C006BEF9C0073EFAD007BE7AD004ABD5A005AC66B0084EFB5007BEF
      AD0073EFA5005ACE6B0039A52900FF00FF00FF00FF00FF00FF00FF00FF004AC6
      6B0052DE7B006BE7940073E79C0052C66B0039AD420039AD42005ACE730084EF
      AD0073E79C0063DE8C0042C6520039A53100FF00FF00FF00FF00FF00FF0042C6
      6B004ACE730063DE8C0052CE730042B55200FF00FF00FF00FF0039B54A0063CE
      7B0084E79C006BDE84004AD66B0039BD420039A53900FF00FF00FF00FF00FF00
      FF004AC673004ACE730042C66B00FF00FF00FF00FF00FF00FF00FF00FF0042B5
      520063CE7B0073DE8C0052D66B0031C6420039AD3900FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF0042BD5A005ACE73005AD66B0042BD520042AD4A00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF0042BD63004AC6630042BD5A00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00
      FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00}
  end
  object chbNoShow: TCheckBox
    Left = 8
    Top = 83
    Width = 137
    Height = 17
    Anchors = [akLeft, akBottom]
    Caption = #1041#1086#1083#1100#1096#1077' '#1085#1077' '#1087#1086#1082#1072#1079#1099#1074#1072#1090#1100
    TabOrder = 2
  end
  object tmrAutoHide: TTimer
    Enabled = False
    OnTimer = tmrAutoHideTimer
    Left = 280
    Top = 8
  end
end
