# 部屋状態チェックツール

Raspberry Pi のセンサー（DHT22 AM2302 など）から部屋の状態を定期チェックして、許容範囲を超えた状態の場合に LINE 通知をするツール。

## 初期設定

```bash
sudo pip3 install -r requirements.txt 
```

## 実行方法

```bash
sudo env LINE_NOTIFY_TOKEN=＜LINE 通知トークン＞ python3 src/main.py
```
