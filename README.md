# Poker
���� ��������� �����

������ 1.0.0

������ ��������

## �������������
����������:
* python 3.6
* pipenv

#### ������
* ������� ���� ������� `config.py` � ����� `poker/server/core`
���������� `config.py.tmpl` � `config.py`

* ��������� ������ � �����

  `poker/server/core/config.py`
  
* ��������� ������ ��������:

  `pipenv run python httpd.py`
  
��������� �������:
* --debug_mode, -dbg: �������� ����� ���������� ����������
* --listen_addr address, -a address: ���� �������. �� ��������� config.LISTEN_ADDR
* --port port, -p port: ���� �������. �� ��������� config.LISTEN_PORT
* --log_file filename, -l filename: ������������� ����� ����� � ��������� ����.
�� ��������� ��������� ����������� ��������� � �������

#### ������
* ���������/�������� ����������� ����� �� ������:
  * `pipenv install`
  * `pipenv update`

* ������� ���� ������� `config.py` � ����� `poker/gui`
���������� `config.py.tmpl` � `config.py`

* ��������� ������ � �����

  `poker/gui/config.py`

* ��������� ����:

  `pipenv run python game.py`