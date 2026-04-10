改动1:品类销售分布下钻到L2功能
后端 (routes/dashboard.py)：                                           
  - 新增 _L2_CODE_MAP — 3位品类代码 →                                    
  名称映射（生鲜/食品/非食品共16个L2品类）                               
  - 新增 _query_category_l2(l1_name) — 按L1过滤，以 LEFT(c_ccode, 3)     
  分组查L2销售                                                           
  - 新增 /api/category_l2?l1=生鲜 接口                                   
  - 扩展 _query_category_hourly — 新增 ccode                             
  参数，直接用前缀长度过滤（2位=L1，3位=L2）                             
  - 更新 /api/category_hourly 接口支持 ?ccode=110 形式                   
                                                                       
  前端 (templates/dashboard.html)：                                      
  - 面板标题区添加返回按钮（默认隐藏）                                   
  - 新增状态变量：categoryLevel、currentL1、currentCategoryCode、DRILLABL
  E_L1                                                                   
  - 点击生鲜/食品/非食品 → 调用                                          
  drillDownCategory()：加载L2图、显示返回按钮、右侧客流图切换到该L1      
  - 点击L2扇形 → 右侧客流图切换到该L2品类                                
  - 点击返回按钮 → drillUpCategory()：还原L1总览，重置右侧图             
  - 门店筛选器切换时自动保持当前层级（L1/L2）                            

改动2:image.png                                            