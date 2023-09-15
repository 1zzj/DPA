# 数据源
### 源图片
(6908,7300)*150 
### 分割方式
512*512 滑动分割

1*源图片 = 210*图像块
### 图像块
(512,512)*31500 

## 训练集 25200

### Annotation__color
(3,512,512)*31500  uint8  颜色
### label
(1,512,512)*31500  uint8  类别
### image
(3,512,512)*31500  uint16  B, G, R, Nir (0-1023?)



## 测试集test 6300



* Correspondence of colors (RGB) and categories: (24个类别)
  200,   0,   0: industrial area 工业区
  0, 200,   0: paddy field  水田
  150, 250,   0: irrigated field  灌溉区
  150, 200, 150: dry cropland  旱地
  200,   0, 200: garden land   园地
  150,   0, 250: arbor forest  乔木林
  150, 150, 250: shrub forest  灌木林
  200, 150, 200: park          公园
  250, 200,   0: natural meadow 天然草地
  200, 200,   0: artificial meadow  人工草地
  0,   0, 200: river          河流
  250,   0, 150: urban residential 城市居民区
  0, 150, 200: lake           湖泊
  0, 200, 250: pond           池塘
  150, 200, 250: fish pond      鱼塘
  250, 250, 250: snow           雪地
  200, 200, 200: bareland       裸地
  200, 150, 150: rural residential 农村居民区 
  250, 200, 150: stadium        体育场
  150, 150,   0: square         广场
  250, 150, 150: road           道路
  250, 150,   0: overpass       立交桥
  250, 200, 250: railway station 火车站
  200, 150,   0: airport         机场
  0,   0,   0: unlabeled       未标注

* Correspondence of indexes and categories:
 1: industrial area
  2: paddy field
  3: irrigated field
  4: dry cropland
  5: garden land
  6: arbor forest
  7: shrub forest
  8: park
  9: natural meadow
   10: artificial meadow
   11: river
   12: urban residential
   13: lake
   14: pond
   15: fish pond
   16: snow
   17: bareland
   18: rural residential
   19: stadium
   20: square
   21: road
   22: overpass
   23: railway station
   24: airport
  0: unlabeled