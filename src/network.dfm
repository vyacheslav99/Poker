object dmNetwork: TdmNetwork
  OldCreateOrder = False
  OnCreate = DataModuleCreate
  OnDestroy = DataModuleDestroy
  Height = 158
  Width = 164
  object MainServer: TIdTCPServer
    Bindings = <
      item
        IP = '0.0.0.0'
        Port = 21000
      end>
    DefaultPort = 0
    OnExecute = MainServerExecute
    Left = 24
    Top = 15
  end
  object MainClient: TIdTCPClient
    ConnectTimeout = 0
    IPVersion = Id_IPv4
    Port = 0
    ReadTimeout = -1
    Left = 88
    Top = 15
  end
  object tmrPing: TTimer
    Enabled = False
    OnTimer = tmrPingTimer
    Left = 24
    Top = 72
  end
  object TestClient: TIdTCPClient
    ConnectTimeout = 0
    IPVersion = Id_IPv4
    Port = 0
    ReadTimeout = -1
    Left = 88
    Top = 71
  end
end
