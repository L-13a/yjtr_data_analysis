---- exec io_getListCol  'vw_tbs_gds' , 'a.' , ' as  ' 
select * from tb_gds where c_name like '%测试%'

--[io]销售客单按时段[T1]
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@分类长度 varchar(20),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max),@开始小时 int, @结束小时 int
select @商品编码='' , @机构='11021',@开始时间='2025-04-26' , @结束时间='2025-04-27',@显示无变动商品='否'
,@部门='',@分类='',@商品名称='',@分类长度='' , @开始小时=0 , @结束小时=23
--exec up_rpt_io_sale_bytime @开始时间 , @结束时间 , '11021' , '11' , '22', '',''
exec up_rpt_io_sale_bytime @开始时间 , @结束时间 , @机构 , @部门 , @开始小时 , @结束小时,@分类, @分类长度,1


/*  
[io]销售客单按时段[T1]  
*/  
alter proc up_rpt_io_sale_bytime(@bdate datetime ,@edate datetime,@c_store_id varchar(max),@c_adno varchar(max),@bhour int,@ehour int,@c_ccode varchar(max),@c_ccodelen varchar(20)='',@init bit=0)    
as  
begin   
 declare @salesum dec(12,2)  , @tmp_c_ccodelen int
 declare @result table (c_store_id varchar(10),c_store_name varchar(20),c_ccode varchar(50),c_ccode_name varchar(50),hours varchar(20),kl int, kd dec(12,2),sale dec(12,2) )  
 if isnull(@init,0)=1
 select @tmp_c_ccodelen=case when @init=1 then codelen else nextcodelen end from io_ccode where name=isnull(@c_ccodelen,'')
 else
 select @tmp_c_ccodelen=case when @init=0 then nextcodelen  end from io_ccode where len(@c_ccode)=codelen
 
 --select @tmp_c_ccodelen=case when @init=1 then @c_ccodelen else @c_ccodelen-1 end
 --print isnull(@tmp_c_ccodelen,99)
 insert into @result  
 select a.c_store_id,c.c_name,substring(b.c_ccode,1,@tmp_c_ccodelen),e.c_name,
 format(DATEPART(HOUR,a.c_datetime),'00'),count(distinct a.c_id),sum(a.c_amount)/count(distinct a.c_id),sum(a.c_amount) 
 from tb_o_sg a  
 left join tb_gds b on a.c_gcode=b.c_gcode  
 left join tb_store c on a.c_store_id=c.c_id  
 left join tb_depart d on a.c_adno=d.c_adno  
 left join tb_gdsclass e on substring(b.c_ccode,1,@tmp_c_ccodelen)=e.c_ccode  
 where a.c_computer_id<>0 and convert(char(10),a.c_datetime,20)>=@bdate and convert(char(10),a.c_datetime,20)<=@edate  
 and a.c_id not like '-%'
 and datepart(hour,a.c_datetime) between @bhour and @ehour 
 and (isnull(@c_store_id,'')='' or a.c_store_id in (select c_str from dbo.uf_io_split_string(@c_store_id,',','store',1,default) ) )  
 and (isnull(@c_adno,'')='' or a.c_adno in (select c_str from dbo.uf_io_split_string(@c_adno,',','adno',1,default) ) )  
 and (isnull(@c_ccode,'')='' or substring(b.c_ccode,1,@tmp_c_ccodelen) like (@c_ccode+'%') )  
 and (a.c_adno<>'14')
 group by a.c_store_id,c.c_name,substring(b.c_ccode,1,@tmp_c_ccodelen),e.c_name,DATEPART(HOUR,a.c_datetime)  
 /*
 -- 按机构,部门,品类进行分组合计
 select c_store_id,c_store_name,c_adno,c_adno_name,c_ccode,c_ccode_name,hours,kl,kd,sale,
 sum(sale) over (partition by c_store_id,c_store_name,c_adno,c_adno_name,c_ccode,c_ccode_name order by hours ) as salesum
 from @result
 group by c_store_id,c_store_name,c_adno,c_adno_name,c_ccode,c_ccode_name,hours,kl,kd,sale
 */
 select c_store_id,c_store_name,c_ccode,c_ccode_name,hours,kl,kd,sale,salesum,bdate,edate,init from (
  select c_store_id,c_store_name,c_ccode,c_ccode_name,hours,kl,kd,sale,
 sum(sale) over (partition by c_store_id order by hours  ) as salesum , @bdate as bdate ,@edate as edate,0 as init
 from @result
 group by c_store_id,c_store_name,
 c_ccode,c_ccode_name,hours,kl,kd,sale
 union all
 select c_store_id,c_store_name,null as c_ccode,null as c_ccode_name,null as hours,sum(kl) as kl,case when sum(kl)<>0 then sum(sale)/sum(kl) else null end as kd,sum(sale) as sale,
 null as salesum,null as bdate,null as edate , null as init
 from @result
 group by c_store_id,c_store_name ) a
 --select @salesum=sum(sale) from @result  
 --select *,@salesum as salesum from @result  order by hours   
 order by case when a.hours IS NULL then 9999 else a.hours end 
end;  


-- [io]总客流日报[T2]
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max)
select @商品编码='001097,001100' , @机构='11021',@开始时间='2025-04-26' , @结束时间='2025-04-27',@显示无变动商品='否',@部门='11',@分类='',@商品名称=''
--select top 100 * from tb_o_sg
select convert(char(10),a.c_datetime,20) as 日期,
case when DATEPART(WEEKDAY, a.c_datetime)=1 then '日' 
	 when DATEPART(WEEKDAY, a.c_datetime)=2 then '一' 
	 when DATEPART(WEEKDAY, a.c_datetime)=3 then '二' 
	 when DATEPART(WEEKDAY, a.c_datetime)=4 then '三' 
	 when DATEPART(WEEKDAY, a.c_datetime)=5 then '四' 
	 when DATEPART(WEEKDAY, a.c_datetime)=6 then '五' 
	 when DATEPART(WEEKDAY, a.c_datetime)=7 then '六' 
end as 星期,
a.c_store_id as 机构,b.c_name as 机构名称,count(distinct a.c_id) as 客流,sum(a.c_amount)/count(distinct a.c_id) as 客单 ,
sum(a.c_amount) as 销售额, sum(a.c_amount)-sum(a.c_pt_cost*c_qtty) as 毛利额,
case when sum(a.c_amount)=0 then null else (sum(a.c_amount)-sum(a.c_pt_cost*c_qtty))/sum(a.c_amount) end as 毛利率
from tb_o_sg a
left join tb_store b on a.c_store_id=b.c_id
where convert(char(10),a.c_datetime,20)>=@开始时间 and convert(char(10),a.c_datetime,20)<=@结束时间
and (isnull(@机构,'')='' or a.c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',')))
 and a.c_id not like '-%'
  and (a.c_adno<>'14')
group by convert(char(10),a.c_datetime,20) , DATEPART(WEEKDAY, a.c_datetime),a.c_store_id , b.c_name 
order by convert(char(10),a.c_datetime,20) , a.c_store_id 

-- 重写换昂捷
-- [io]品类销售分析表T3
declare @品类层次 int , @开始日期 datetime, @结束日期 datetime,@分类 varchar(1000),  @机构 varchar(max), @c_ccode varchar(20)
select @品类层次=null , @开始日期='2026-01-04' , @结束日期='2026-01-04' ,@机构='11021',@分类=''  ;
--select * from tb_gdsclass
-- select * from tb_gdsstore where c_sale_status in ('暂停销售') and c_status in ('作废','暂停进货')
--select * from dbo.io_get_gds_gcode_cnt(@机构,11,@开始日期,@结束日期) where c_sale_status in ('暂停销售')
with temp00 as(
select gc.c_ccode ,gc.c_level,gc.c_name  
,count(distinct g.c_gcode) as c_kind
,count(distinct case when isnull(g.c_sale,0)<>0 then g.c_gcode else null end) as 动销数
,round(cast(count(distinct case when isnull(g.c_sale,0)<>0 then g.c_gcode else null end) as dec(12,2))/count(distinct g.c_gcode),4) as 动销率
,count(distinct g.c_gcode)-count(distinct case when isnull(g.c_sale,0)<>0 then g.c_gcode else null end) as 不动销数
from tb_gdsclass  gc
cross apply dbo.io_get_gds_gcode_cnt(@机构,gc.c_ccode,@开始日期,@结束日期) g
where (isnull(@品类层次,'')='' or gc.c_level=@品类层次)
and (isnull(@分类,'')='' or gc.c_ccode = @分类)
and gc.c_ccode not like '44%' 
and g.c_sale_status not in ('暂停销售') 
--and g.c_status not in ('作废','暂停进货')
and not (g.c_number=0 and g.c_status  in ('暂停进货') )
and gc.c_ccode=g.c_ccode_pre 
group by gc.c_ccode ,gc.c_level,gc.c_name  
)  select * from temp00    ,
temp01 as(
select gc.c_ccode, gc.c_name as 品类名称, sum(ds.c_sale)  as 销售额, sum(ds.c_sale)-sum(ds.c_at_sale) as 毛利额,
case when sum(ds.c_sale)=0 then null else (sum(ds.c_sale)-sum(ds.c_at_sale))/sum(ds.c_sale) end as 毛利率,
sum(ds.c_sale_count) as 来客数,case when sum(ds.c_sale_count)=0 then null else (sum(ds.c_sale)-0)/sum(ds.c_sale_count) end as 客单价,
sum(ds.c_at_sale) as c_at_sale
from tb_gdsclass  gc 
left join tbs_d_supp ds on ds.c_type='品类' and ds.c_dt>=@开始日期 and ds.c_dt<=@结束日期 and ds.c_id=gc.c_ccode
and  ds.c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default) ) 
where (isnull(@品类层次,'')='' or gc.c_level=@品类层次)
and (isnull(@分类,'')='' or gc.c_ccode=@分类)
and gc.c_ccode not like '44%'
group by gc.c_ccode, gc.c_name
)  ,
temp02 as (
select a.c_ccode,a.品类名称,a.销售额,a.毛利额,a.毛利率,a.来客数,a.客单价,
b.c_kind as 品项数,b.动销数 as 动销数,b.动销率 as 动销率,b.不动销数 as 不动销数,c.c_sale as c_sale_par,c.c_maoli as c_maoli_par,
(select sum(c_sale) as c_sale from tbs_d_supp  
	where c_type='机构' and c_dt>=@开始日期 and c_dt<=@结束日期 
	and  c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default) ) ) as c_store_sale,
	(select sum(c_sale)-sum(c_at_sale) as c_sale from tbs_d_supp  where c_type='机构' and c_dt>=@开始日期 and c_dt<=@结束日期 
		and  c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default) ) ) as c_store_maoli
from temp01 a 
left join temp00 b on a.c_ccode=b.c_ccode
left join (
select c_id ,sum(c_sale) as c_sale,sum(c_sale-c_at_sale) as c_maoli from tbs_d_supp  where c_type='品类' and c_dt>=@开始日期 and c_dt<=@结束日期 
and  c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default) ) group by c_id
) c on  case when len(a.c_ccode)=3 then substring(a.c_ccode,1,len(a.c_ccode)-1) else substring(a.c_ccode,1,len(a.c_ccode)-2) end=c.c_id
) 
/*----++++*/

select  a.c_ccode as 品类号码,len(a.c_ccode) as 品类长度,a.品类名称 as 品类名称,a.销售额 as 销售额,a.毛利额 as 毛利额,a.毛利率 as 毛利率,a.来客数 as 来客数 ,a.客单价 as 客单价
,a.品项数 as 品项数,a.动销数 as 动销数,a.动销率 as 动销率,a.不动销数 as 不动销数
,case when a.c_sale_par=0 then null else a.销售额/a.c_sale_par end as 销售额占比_课占部
,case when a.c_store_sale=0 then null else a.销售额/a.c_store_sale end as 销售额占比_课占店
,case when a.c_maoli_par=0 then null else a.毛利额/a.c_maoli_par end as 毛利额占比_课占部
,case when a.c_store_maoli=0 then null else a.毛利额/a.c_store_maoli end as 毛利额占比_课占店
from temp02 a
where 1=1
and (isnull(@分类,'')='' or a.c_ccode=@分类)
order by a.c_ccode

--  [io]不动销商品明细T3.1   不独立使用,给T3做跳转
declare @品类层次 int , @开始日期 datetime, @结束日期 datetime,@分类 varchar(1000),  @机构 varchar(max), @c_ccode varchar(20)
select @品类层次=null , @开始日期='2026-01-04' , @结束日期='2026-01-04' ,@机构='11021',@分类='11'  ;
--select * from tb_gdsclass
-- select * from tb_gdsstore where c_sale_status in ('暂停销售') and c_status in ('作废','暂停进货')
--select * from dbo.io_get_gds_gcode_cnt(@机构,11,@开始日期,@结束日期) where c_sale_status in ('暂停销售')

select g.c_store_id as 机构编码,g.c_gcode as 商品编码,g.c_adno as 部门编码,g.c_name as 商品名称,g.c_barcode as 商品条码,g.c_basic_unit as 单位,
g.c_model as 规格,g.c_pt_cost as 进价,g.c_price as 售价,g.c_ccode as 品类编码,gc.c_name 品类名称,g.c_status as 商品状态,g.c_sale_status as 销售状态 , 
g.c_number as 库存,
g.c_sale as 销售
from tb_gdsclass  gc
cross apply dbo.io_get_gds_gcode_cnt(@机构,gc.c_ccode,@开始日期,@结束日期) g
where (isnull(@品类层次,'')='' or gc.c_level=@品类层次)
and (isnull(@分类,'')='' or gc.c_ccode = @分类)
and gc.c_ccode not like '44%' 
and g.c_sale_status not in ('暂停销售') 
--and g.c_status not in ('作废','暂停进货')
and not (g.c_number=0 and g.c_status  in ('暂停进货') )
and gc.c_ccode=g.c_ccode_pre 
and isnull(g.c_sale,0)=0

-- [io]动销商品明细T3.2     不独立使用,给T3做跳转
declare @品类层次 int , @开始日期 datetime, @结束日期 datetime,@分类 varchar(1000),  @机构 varchar(max), @c_ccode varchar(20)
select @品类层次=null , @开始日期='2026-01-04' , @结束日期='2026-01-04' ,@机构='11021',@分类='11'  ;
--select * from tb_gdsclass
-- select * from tb_gdsstore where c_sale_status in ('暂停销售') and c_status in ('作废','暂停进货')
--select * from dbo.io_get_gds_gcode_cnt(@机构,11,@开始日期,@结束日期) where c_sale_status in ('暂停销售')

select g.c_store_id as 机构编码,g.c_gcode as 商品编码,g.c_adno as 部门编码,g.c_name as 商品名称,g.c_barcode as 商品条码,g.c_basic_unit as 单位,
g.c_model as 规格,g.c_pt_cost as 进价,g.c_price as 售价,g.c_ccode as 品类编码,gc.c_name 品类名称,g.c_status as 商品状态,g.c_sale_status as 销售状态 , 
g.c_number as 库存,
g.c_sale as 销售
from tb_gdsclass  gc
cross apply dbo.io_get_gds_gcode_cnt(@机构,gc.c_ccode,@开始日期,@结束日期) g
where (isnull(@品类层次,'')='' or gc.c_level=@品类层次)
and (isnull(@分类,'')='' or gc.c_ccode = @分类)
and gc.c_ccode not like '44%' 
and g.c_sale_status not in ('暂停销售') 
--and g.c_status not in ('作废','暂停进货')
and not (g.c_number=0 and g.c_status  in ('暂停进货') )
and gc.c_ccode=g.c_ccode_pre 
and isnull(g.c_sale,0)<>0
order by g.c_sale

--品类名称	销售额	毛利额	毛利率	来客数	客单价	品项数	动销品项数	动销率	销售额占比（课占店）	销售占比（课占部）	毛利额占比（课占店）	毛利额占比（课占部）	部门占门店比


--[io]销售时段对比[T4]
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime
select @商品编码='001097,001100' , @机构='11021',@开始时间='2025-04-28' , @结束时间='2025-04-28',@显示无变动商品='否',@部门='11',@分类='',@商品名称=''
,@对比开始时间='2025-03-25' , @对比结束时间='2025-03-25' ;

--ltrim(str((cast(b.count_id as dec(12,2))-cast(a.count_id as dec(12,2))/a.count_id*100))+'%'

with temp00 as (
select a.c_hour as 时段, 
a.c_amount as 销售额,a.count_id as 客流, a.kd as 客单,
b.c_amount as 对比销售额,b.count_id as 对比客流,b.kd as 对比客单,
a.c_amount-b.c_amount as 销售差,
case when a.c_amount=0 then null else (a.c_amount-isnull(b.c_amount,0))/a.c_amount end as 销售对比率,
a.count_id-b.count_id as 客流差,
a.kd-b.kd as 客单差
from 
(
select FORMAT(c_datetime,'HH') as c_hour ,sum(c_amount) as c_amount,count(distinct c_id) as count_id,
sum(c_amount)/ case when count(distinct c_id)=0 then null else count(distinct c_id) end as kd from tb_o_sg 
where c_computer_id<>0 and convert(char(10),c_datetime,20)>=@开始时间 and convert(char(10),c_datetime,20)<=@结束时间
and (isnull(@机构,'')='' or c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',')))
and c_id not like '-%' and (c_adno<>'14')
group by FORMAT(c_datetime,'HH')
) a 
left join (
select FORMAT(c_datetime,'HH') as c_hour ,sum(c_amount) as c_amount,count(distinct c_id) as count_id,
sum(c_amount)/ case when count(distinct c_id)=0 then null else count(distinct c_id) end as kd from tb_o_sg 
where c_computer_id<>0 and convert(char(10),c_datetime,20)>=@对比开始时间 and convert(char(10),c_datetime,20)<=@对比结束时间
and (isnull(@机构,'')='' or c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',')))
and c_id not like '-%'  and (c_adno<>'14')
group by FORMAT(c_datetime,'HH')
) b on a.c_hour=b.c_hour
)

/*----++++*/

select 时段 as 时段,销售额 as 销售额,客流 as 客流,客单 as 客单,对比销售额 as 对比销售额,对比客流 as 对比客流,对比客单 as 对比客单,销售差 as 销售差,销售对比率 as 销售对比率 ,客流差 as 客流差,客单差 as 客单差 from (
	select 时段,销售额,客流,客单,对比销售额,对比客流,对比客单,销售差,销售对比率,客流差,客单差 from temp00
	union all
	select null as 时段,sum(销售额) as 销售额,sum(客流) as 客流,
	case when sum(客流)=0 then null else sum(销售额)/sum(客流)  end as 客单,
	sum(对比销售额) as 对比销售额,sum(对比客流) as 对比客流,
	case when sum(对比客流)=0 then null else  sum(对比销售额)/sum(对比客流) end as 对比客单,
	sum(销售额)-sum(对比销售额) as 销售差,
	case when sum(销售额)=0 then null else sum(销售额)-sum(对比销售额) / sum(销售额) end as 销售对比率,
	sum(客流)-sum(对比客流) as 客流差,
	case when sum(客流)=0 then null else sum(销售额)/sum(客流)  end - case when sum(对比客流)=0 then null else  sum(对比销售额)/sum(对比客流) end as 客单差 
	from temp00
) a where 1=1 
order by case when a.时段 IS NULL then 9999 else a.时段 end 






-- [io]畅销商品缺货[T5]
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) ,@预警天数 int,@销售频率 varchar(50),@供应商类型 varchar(100)
select @商品编码='' , @机构='11026',@部门='',@分类='22',@商品名称='',@预警天数=7,@销售频率='全部' , @供应商编码='' , @供应商类型=''
--select top 100 c_sn_perday,* from tb_gdsstore where c_gcode='041498' c_sn_perday<>0
-- select top 100 * from tb_gds 

select  gs.c_gcode as 商品编码,g.c_name as 商品名称,g.c_barcode as 商品条码,g.c_model as 规格,g.c_basic_unit as 单位,
gs.c_status as 商品状态,gs.c_pro_status as 促销状态,gs.c_sale_frequency as 销售频率,
gs.c_pt_cost as 进价,case when gs.c_price_disc=0 then gs.c_price else gs.c_price_disc end  as 售价
,case  when gs.c_price_disc=0 then gs.c_price-gs.c_pt_cost else gs.c_price_disc-gs.c_pt_cost end  as 毛利
,dbo.io_div(case when gs.c_price_disc=0 then gs.c_price-gs.c_pt_cost else gs.c_price_disc-gs.c_pt_cost end,
case when gs.c_price_disc=0 then gs.c_price else gs.c_price_disc end,4) as 毛利率
,gs.c_number as 库存,gs.c_at_cost as 库存金额,c_lastsale_dt as 最后销售日期,gs.c_sn_perday as 日均销售,c_onway as 在途,gc.c_ccode as 品类编码,gc.c_name as 品类名称
,gs.c_provider as 主供应商编码,p.c_name as 供应商名称,p.c_category as 供应商类型
from tb_gdsstore gs
left join tb_gds g on g.c_gcode=gs.c_gcode
left join tb_gdsclass gc on g.c_ccode=gc.c_ccode
left join tb_partner p on gs.c_provider=p.c_no
where
(isnull(@商品编码,'')='' or gs.c_gcode in (select c_str from  dbo.uf_split_string(isnull(@商品编码,''),',') )) 
and (isnull(@机构,'')='' or gs.c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',') ))
and (isnull(@分类,'')='' or gc.c_ccode like @分类+'%')
and (isnull(@供应商编码,'')='' or gs.c_provider=@供应商编码)
and (isnull(@供应商类型,'')='' or p.c_category like '%'+@供应商类型+'%')
and gs.c_number<gs.c_sn_perday*@预警天数
and gs.c_adno not in ('13','14')
and gs.c_type like '自营%'
and gs.c_status not in ('作废')
and not (gs.c_status in ('暂停进货') and isnull(gs.c_number,0)=0)
and (isnull(@销售频率,'')='' or isnull(@销售频率,'')='全部' or gs.c_sale_frequency = @销售频率)

select distinct c_category from tb_partner where c_category like '%自采%'
select * from tb_gdsstore where c_store_id='11026' and c_gcode='073309'

-- [io]商品销售分析T6
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@品类编码 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime , @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11021',@开始时间='2025-04-28' , @结束时间='2025-05-28',@显示无变动商品='否',@部门='11',@品类编码='',@商品名称='',@预警天数=3,@销售频率='畅销', @供应商编码='' ;
select dg.c_gcode as 商品编码,g.c_name as 商品名称,g.c_barcode as 商品条码,g.c_model as 规格,g.c_basic_unit as 单位,(dg.c_number_sale) as 销售数量 ,(dg.c_sale) as 销售额, 
dg.c_at_sale as 成本,dg.maoli as 毛利,dg.maoliv as 毛利率,
gc.c_ccode as 品类编码,gc.c_name as 品类名称,p.c_no as 供应商编码,p.c_name as 供应商名,(gs.c_number) as 当前库存,gs.c_number-isnull(sg.c_qtty,0) as 实时库存,sg.c_qtty as 当前销售
from (
	select c_store_id,c_gcode,sum(c_number_sale) as c_number_sale,sum(c_sale) as c_sale,sum(c_at_sale) as c_at_sale,
	sum(c_sale-c_at_sale ) as maoli,
	case when sum(c_sale)=0 then null else sum(c_sale-c_at_sale )/sum(c_sale) end as maoliv
	from tbs_d_gds dg
	where convert(char(10),c_dt,20)>=@开始时间 and convert(char(10),c_dt,20)<=@结束时间
	and (isnull(@机构,'')='' or c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',') ))
	and c_adno not in ('13','14')
	group by c_store_id,c_gcode
) dg
left join (
	select c_store_id ,c_gcode,c_provider,c_number from tb_gdsstore 
	where (isnull(@机构,'')='' or c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',') ))
) gs on  dg.c_store_id=gs.c_store_id  and dg.c_gcode=gs.c_gcode 
left join (
	select c_store_id ,c_gcode,sum(c_qtty) as c_qtty from tb_o_sg 
	where convert(char(10),c_datetime,20)>=convert(char(10),getdate(),20) and convert(char(10),c_datetime,20)<=convert(char(10),getdate(),20)
	and (isnull(@机构,'')='' or c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',') ))
	group by c_store_id ,c_gcode
) sg on dg.c_store_id=sg.c_store_id  and dg.c_gcode=sg.c_gcode 
left join tb_gds g on dg.c_gcode=g.c_gcode
left join tb_gdsclass gc on g.c_ccode=gc.c_ccode
--left join tb_contract c on dg.c_con_no=c.c_con_no
left join tb_partner p on gs.c_provider=p.c_no
where 1=1 --convert(char(10),dg.c_dt,20)>=@开始时间 and convert(char(10),dg.c_dt,20)<=@结束时间
and (isnull(@机构,'')='' or dg.c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',') ))
and (isnull(@商品编码,'')='' or dg.c_gcode=@商品编码)
and (isnull(@部门,'')='' or g.c_adno=@部门)
and (isnull(@品类编码,'')='' or g.c_ccode=@品类编码)
and (isnull(@供应商编码,'')='' or p.c_no=@供应商编码)


-- [io]供应商到货率汇总T7
  declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime , @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11026',@开始时间='2025/10/01' , @结束时间='2025/10/06',@供应商编码='12096',@显示无变动商品='否',@部门='11',@分类='',@商品名称='',@预警天数=3,@销售频率='畅销' ;

with temp00 as (
	select p.c_no ,p.c_name ,sum(dg.c_sale) as c_sale,sum(dg.c_sale-dg.c_at_sale) as c_maoli ,
	case when sum(dg.c_sale)=0 then null else 1.00*sum(dg.c_sale-dg.c_at_sale)/sum(dg.c_sale) end as c_maoliv,
	gp.count_gcode as kind_count,
	count(distinct dg.c_gcode) as dongxiao,
	case when sum(gp.count_gcode)=0 then null else 1.00*count(distinct dg.c_gcode)/gp.count_gcode end as dongxiaov
	from tbs_d_gds dg
	left join tb_contract c on dg.c_con_no=c.c_con_no
	left join tb_partner p on c.c_provider=p.c_no
	left join (
	select c_provider,count(distinct c_gcode)  count_gcode 
	from tb_gdsprovider where c_status_gp='正常进货' 
	and (isnull(@机构,'')='' or c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default)))
	and (isnull(@供应商编码,'')='' or c_provider=@供应商编码)
	group by c_provider 
	) gp on p.c_no=gp.c_provider  --and dg.c_gcode=gp.c_gcode
	where 1=1 
	and convert(char(10),dg.c_dt,20)>=@开始时间 and convert(char(10),dg.c_dt,20)<=@结束时间
	and (isnull(@机构,'')='' or dg.c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default)))
	and not (dg.c_store_id='11016' and convert(char(10),dg.c_dt,20)>='2025-08-01')
	and (isnull(@供应商编码,'')='' or p.c_no=@供应商编码)
	group by p.c_no,p.c_name , gp.count_gcode ) 
	,
temp_oi as (
select a.c_provider,sum(isnull(b.c_order_n,0)) as c_order_n,sum(isnull(b.c_order_n,0)*isnull(c_pt_in,0)) as c_order_am
,sum(isnull(c_rec_n,0)) as c_rec_n,sum(isnull(c_rec_n,0)*isnull(c_pt_in,0)) as c_rec_am 
from tb_o_i a, tb_o_ig b where a.c_id=b.c_id 
and convert(char(10),a.c_rec_au_dt,20)>=@开始时间 and convert(char(10),a.c_rec_au_dt,20)<=@结束时间 
and not (a.c_delivery_store_id='11016' and convert(char(10),a.c_rec_au_dt,20)>='2025-08-01')
and (isnull(@供应商编码,'')='' or a.c_provider=@供应商编码)
and a.c_rec_type='有订单收货'
  and a.c_rec_status='收货已审核'
  and c_at_order<>0
group by a.c_provider)

/*----++++*/
select a.c_no as 供应商号,a.c_name as 供应商名称,a.c_sale as 销售额
,a.c_maoli as 毛利,a.c_maoliv as 毛利率,a.kind_count as 品项数,a.dongxiao as 动销数,a.dongxiaov as 动销率
,b.c_order_n as 订货量,b.c_order_am as 订货额,b.c_rec_n as 到货量,b.c_rec_am as 到货额
,case when b.c_order_n=0 then null else 1.00*b.c_rec_n/b.c_order_n end as 到货量率
,case when b.c_order_am=0 then null else 1.00*b.c_rec_am/b.c_order_am end as 到货额率
from temp00 a,temp_oi b where a.c_no=b.c_provider


--[io]负毛利T8
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime , @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11026',@开始时间='2025-09-01' , @结束时间='2025-09-17',@部门='',@分类='226'
-- select * from tbs_d_gds where c_dt>='2025-09-01' and c_store_id='11026' and c_gcode='092042'
drop table #temp01
	select c_store_id ,convert(char(10),c_datetime,20) as c_dt,c_gcode,sum(c_pt_cost*c_qtty) as c_at_cost 
	into #temp01 from tb_o_sg 
		where convert(char(10),c_datetime,20)>=@开始时间
		and convert(char(10),c_datetime,20)<=@结束时间
		and (isnull(@机构,'')='' or c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default) ))
		and c_id like '-%'
		group by c_store_id ,c_gcode,convert(char(10),c_datetime,20)
/*----++++*/
  select dg.c_store_id as 机构编码,s.c_name as 机构名称,dg.c_name as 商品名称,g.c_gcode as 商品编码,g.c_barcode as 条码,g.c_model as 规格,g.c_basic_unit as 单位,
  dg.c_dt as 销售日期,
  dg.c_number_sale as 销售数量,dg.c_sale as 销售金额,dg.c_at_sale-isnull(sg.c_at_cost,0) as 成本金额, sg.c_at_cost as 勾兑成本,
  dg.c_sale-(dg.c_at_sale-isnull(sg.c_at_cost,0)) as 毛利额,
  dg.c_pt_cost as 进价,dg.c_price as 售价,(dg.c_sale-(dg.c_at_sale-isnull(sg.c_at_cost,0))) as 毛利 ,gs.c_number as 库存,
  case when isnull(dg.c_sale,0)=0 then null else (dg.c_sale-(dg.c_at_sale-isnull(sg.c_at_cost,0)))/(dg.c_sale) end as 毛利率,
  gs.c_lastin_dt as 最后收货日期,gs.c_lastsale_dt as 最后销售日期,
  gc.c_name as 分类,p.c_name as 供应商
  from tbs_d_gds dg
left join tb_gds g on g.c_gcode=dg.c_gcode
left join tb_gdsstore gs on gs.c_store_id=dg.c_store_id and gs.c_gcode=dg.c_gcode
left join tb_gdsclass gc on gc.c_ccode=g.c_ccode
left join tb_partner p on p.c_no=gs.c_provider
left join tb_store s on dg.c_store_id =s.c_id
left join (
	select * from #temp01
) sg on dg.c_store_id =sg.c_store_id and dg.c_dt =sg.c_dt and dg.c_gcode=sg.c_gcode
where convert(char(10),dg.c_dt,20)>=@开始时间 and convert(char(10),dg.c_dt,20)<=@结束时间
and (isnull(@机构,'')='' or dg.c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default) ))
and (isnull(@部门,'')='' or gs.c_adno =@部门)
and (isnull(@分类,'')='' or g.c_ccode like @分类+ '%')
and gs.c_type like '%自营%'
and (dg.c_sale-(dg.c_at_sale-isnull(sg.c_at_cost,0))) <0
and isnull(dg.c_sale,0)<>0


/*
select c_lastin_dt,c_lastsale_dt,* from tb_gdsstore where c_gcode='008300' and c_store_id='11021'
select * from tb_gdsprovider where c_provider='12012' and c_store_id='11026' and c_gcode='001541'
select distinct c_store_status from tb_gdsstore

select * from tb_partner
*/
--[io]高库存(低周转)T9
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime , @安全天数 int,@销售频率 varchar(50),@计算公式 varchar(100)
select @商品编码='' , @机构='11023',@开始时间='2025-04-28' , @结束时间='2025-05-01',@显示无变动商品='否',@部门='11',@分类='',@商品名称='',@安全天数=3,@销售频率='畅销'
,@计算公式='基于周转天数' --基于周转天数  基于安全天数  
--品名	条码	规格	单位	新品日	商品品态	促销	畅销	进价	售价	毛利率	库存数量	库存成本	日均销量	库存天数	最后收货日期	最后销售日期	分类名称	供应商名称
--select * from tb_gdsstore where c_gcode='041725'
select g.c_ccode as 品类,g.c_name as 品名,g.c_barcode as 条码,g.c_model as 规格,gs.c_introduce_date as 新品日,
gs.c_status as 商品品态,gs.c_pro_status as 促销,gs.c_sale_frequency as 畅销, gs.c_pt_cost as 进价,
gs.c_price as 售价, 
case when gs.c_price=0 then null else (gs.c_price-gs.c_pt_cost)/gs.c_price end as 毛利率,
gs.c_number as 库存数量,gs.c_at_cost as 库存成本,
gs.c_sn_perday as 日均销量,gs.c_dnlmt_day as 安全库存天数,0 as w滞销天数,gs.c_lastin_dt as 最后收货日期,gs.c_lastsale_dt as 最后销售日期,
gc.c_name as 分类名称, p.c_name as 主供应商名称
,g.c_adno as 部门,dg.c_sale as 最近年销售,c_sale_day as 年平均销售, --dbo.io_div(gs.c_at_cost,dg.c_sale_day,4)
case when dg.c_sale_day=0 then null else gs.c_at_cost/dg.c_sale_day end as 计算值
from tb_gdsstore gs
left join tb_gds g on g.c_gcode=gs.c_gcode
left join tb_gdsclass gc on gc.c_ccode=g.c_ccode 
left join tb_partner p  on p.c_no=gs.c_provider
left join (
	select c_store_id,c_gcode,sum(c_sale) as c_sale,sum(c_sale)/12/30 as c_sale_day from tbs_d_gds 
	where convert(char(10),c_dt,20) between dateadd(year,-1,convert(char(10),getdate()-1,20)) and convert(char(10),getdate()-1,20)
	group by c_store_id,c_gcode
) dg on dg.c_store_id=gs.c_store_id and dg.c_gcode=gs.c_gcode
where  (isnull(@机构,'')='' or gs.c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1 , default ) ) )
and (isnull(@分类,'')='' or g.c_ccode like @分类 +'%' )
and g.c_ccode not like '44%'
and gs.c_type like '自营%'
and (gs.c_status not in ('作废') )
and not (gs.c_status in ('暂停进货') and gs.c_number=0)
and (1=0
or (@计算公式='基于周转天数' 
		and	case when g.c_adno=13 and case when dg.c_sale_day=0 then null else gs.c_at_cost/dg.c_sale_day end >5 then 1 
				 when g.c_adno=11 and case when dg.c_sale_day=0 then null else gs.c_at_cost/dg.c_sale_day end>30 then 1 
				 when g.c_adno=12 and case when dg.c_sale_day=0 then null else gs.c_at_cost/dg.c_sale_day end>60 then 1 
			else 0 end =1)
or (@计算公式='基于安全天数' 
		and	 case when gs.c_sn_perday=0 then null else gs.c_number/gs.c_sn_perday end < @安全天数 ) --dbo.io_div(gs.c_number,gs.c_sn_perday,4)<@安全天数)
		)
order by gs.c_number

-- select top 10 * from tbs_d_gds where c_status in ('作废','暂停进货')

select dateadd(year,-1,convert(char(10),getdate()-1,20))
--[io]新品报表T10
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime , @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11021',@开始时间='2025-04-28' , @结束时间='2025-04-28',@显示无变动商品='否',@部门='11',@分类='',@商品名称='',@预警天数=3,@销售频率='畅销'
--品名	条码	规格	单位	新品日	首次进货日期	首次销售日期	新品天数	商品品态	促销	畅销	供应商名称	
--销售数量	销售金额	销售毛利	销售毛利率	库存数量	库存成本	日均销售	在途数量	库存天数	分类名称
select g.c_gcode as 商品编码,g.c_name as 商品名, g.c_barcode as 条码,g.c_model as 规格,g.c_basic_unit as 单位,gs.c_introduce_date as 新品日,
gs.c_first_order_dt as 首次进货日期,gs.c_firstsale_dt as 首次销售日期,gs.c_test_day as 新品天数,
gs.c_status as 商品品态,gs.c_pro_status as 促销,gs.c_sale_frequency as 畅销,gs.c_provider as 供应商名称,
dg.c_number_sale as 销售数量, dg.c_sale as 销售金额,dg.c_maoli as 销售毛利,dg.c_maoliv as 销售毛利率,
gs.c_number as 库存数量,gs.c_at_cost as 库存成本,gs.c_sn_perday as 日均销售,gs.c_onway as 在途数量,gs.c_dnlmt_day as 库存天数,gc.c_name as 分类名称
from tb_gdsstore gs
left join tb_gds g on g.c_gcode=gs.c_gcode
left join tb_gdsclass gc on g.c_ccode=gc.c_ccode
left join (
	select c_store_id ,c_gcode,sum(c_number_sale) as c_number_sale,sum(c_sale) as c_sale,sum(c_sale-c_at_sale) as c_maoli,
	case when sum(c_sale)=0 then null else sum(c_sale-c_at_sale)/sum(c_sale) end as c_maoliv
	from tbs_d_gds where convert(char(10),c_dt,20)>=@开始时间 and convert(char(10),c_dt,20)<=@结束时间
	and (isnull(@机构,'')='' or c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',') ))
	group by c_store_id ,c_gcode
) dg on dg.c_store_id=gs.c_store_id and dg.c_gcode=gs.c_gcode 
where 1=1
and (isnull(@机构,'')='' or gs.c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',') ))
and gs.c_status not in ('暂停进货','正常流转','作废')
and isnull(gs.c_test_day,0)<>0
and gs.c_type like '%自营%'
--and gs.c_status='试销期'
and datediff(day,gs.c_introduce_date,getdate()) <g.c_od_day

select * from tb_gds where c_gcode='008300'
select * from tb_gdsstore where c_gcode='008300' and c_store_id='11021'
select datediff(day,getdate()-2,getdate())

-- [io]供应商动销率T11.1
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime , @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11007',@开始时间='2025-05-01' , @结束时间='2025-05-19',@显示无变动商品='否',@部门='11',@分类='',@商品名称='',@预警天数=3,@销售频率='畅销',
@供应商编码='12002' ;   -- 89	4	85

select gdsp.c_store_id as 机构,s.c_sname as 机构名称,gdsp.c_provider as 供应商号,p.c_name as 供应商名称,
count(distinct gdsp.c_gcode) as 单品数 ,count(case when dg.c_sale is null then null else 1 end ) as 动销数
,count(case when dg.c_sale is not null then null else 1 end ) as 不动销数,
--count(case when dg.c_sale is null then null else 1 end ) / count(distinct gdsp.c_gcode) as 动销率,
--dbo.io_div(count(case when dg.c_sale is null then null else 1 end ) , count(distinct gdsp.c_gcode) ,4) as 动销率2,
cast(count(case when dg.c_sale is null then null else 1 end ) as float) / cast(count(distinct gdsp.c_gcode) as float) as 动销率
from tb_gdsprovider gdsp
left join (
	select dg.c_store_id,dg.c_gcode,sum(dg.c_at_sale) as c_at_sale,sum(dg.c_sale) as c_sale from tbs_d_gds dg 
	where convert(char(10),dg.c_dt,20)>=@开始时间 and convert(char(10),dg.c_dt,20)<=@结束时间
	group by dg.c_store_id,dg.c_gcode
) dg on dg.c_gcode=gdsp.c_gcode and dg.c_store_id=gdsp.c_store_id 
inner join tb_store s on s.c_id=gdsp.c_store_id and s.c_status='正常营业'
left join tb_partner p on gdsp.c_provider=p.c_no
left join tb_gds g on g.c_gcode=gdsp.c_gcode and (isnull(@分类,'')='' or g.c_ccode like @分类+'%')
left join tb_gdsclass gc on gc.c_ccode=g.c_ccode
left join tb_gdsstore gs on gs.c_store_id=gdsp.c_store_id and gs.c_gcode=gdsp.c_gcode
where gdsp.c_status_gp='正常进货'  and gs.c_status not in ('暂停销售')
and (isnull(@机构,'')='' or gdsp.c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1 ,default ) ))
and (isnull(@供应商编码,'')='' or gdsp.c_provider=@供应商编码)
and (isnull(@分类,'')='' or g.c_ccode like @分类+'%')
group by gdsp.c_store_id,s.c_sname,gdsp.c_provider,p.c_name 



-- [io]供应商动销明细T11.1  and dg.c_sale is not null  -- [io]供应商不动销明细T11.1   两个报表的语句一样and dg.c_sale is null
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime , @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11007',@开始时间='2025-05-01' , @结束时间='2025-05-19',@显示无变动商品='否',@部门='11',@分类='',@商品名称='',@预警天数=3,@销售频率='畅销',
@供应商编码='12002' ;   -- 89	4	85


select gdsp.c_store_id as 机构,s.c_sname as 机构名称,gdsp.c_provider as 供应商号,p.c_name as 供应商名称,gdsp.c_gcode as 商品编码,
g.c_name as 商品名称,g.c_ccode as 分类编码,gc.c_name as 分类名称,g.c_model as 规格,g.c_basic_unit as 单位, 
gs.c_pt_cost as 合同进价,gs.c_price as 售价, case when gs.c_price=0 then null else (gs.c_price-gs.c_pt_cost)/gs.c_price end as 毛利率, 
gs.c_lastsale_dt as 最后销售日期,gs.c_lastin_dt as 最后进货日期,sum(gs.c_number) as 库存,
sum(dg.c_at_sale) as 进价金额,sum(dg.c_sale) as 售价金额 from tb_gdsprovider gdsp
left join (
	select dg.c_store_id,dg.c_gcode,sum(dg.c_at_sale) as c_at_sale,sum(dg.c_sale) as c_sale from tbs_d_gds dg 
	where convert(char(10),dg.c_dt,20)>=@开始时间 and convert(char(10),dg.c_dt,20)<=@结束时间
	group by dg.c_store_id,dg.c_gcode
) dg on dg.c_gcode=gdsp.c_gcode and dg.c_store_id=gdsp.c_store_id 
inner join tb_store s on s.c_id=gdsp.c_store_id and s.c_status='正常营业'
left join tb_partner p on gdsp.c_provider=p.c_no
left join tb_gds g on g.c_gcode=gdsp.c_gcode
left join tb_gdsclass gc on gc.c_ccode=g.c_ccode
left join tb_gdsstore gs on gs.c_store_id=gdsp.c_store_id and gs.c_gcode=gdsp.c_gcode
where gdsp.c_status_gp='正常进货' and gs.c_status not in ('暂停销售') --and  isnull(dg.c_sale,0)<>0
and (isnull(@机构,'')='' or gdsp.c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default ) ))
and (isnull(@供应商编码,'')='' or gdsp.c_provider=@供应商编码)
and (isnull(@分类,'')='' or g.c_ccode like @分类+'%')
and dg.c_sale is null
group by gdsp.c_store_id,s.c_sname,gdsp.c_gcode,g.c_name,g.c_ccode,gdsp.c_provider,p.c_name,gc.c_name,g.c_model,g.c_basic_unit,gs.c_pt_cost,gs.c_price,dg.c_sale,gs.c_lastsale_dt,gs.c_lastin_dt
--having sum(gs.c_number)<>0
order by gdsp.c_provider,gdsp.c_store_id

-- select top 1 * from tb_gdsstore
-- select * from tb_gdsprovider
select dg.c_store_id as 机构,s.c_sname as 机构名称,dg.c_gcode,p.c_no as 供应商编码,p.c_name as 供应商名称,dg.c_gcode as 商品编码,g.c_name as 商品名称,
sum(c_at_sale) as 进价金额,sum(dg.c_sale) as 销售金额,sum(dg.c_sale)-sum(c_at_sale) as 毛利
from tbs_d_gds dg
left join tb_contract c on dg.c_con_no=c.c_con_no
left join tb_partner p on c.c_provider=p.c_no
left join tb_store s on dg.c_store_id=s.c_id
left join tb_gds g on g.c_gcode=dg.c_gcode
left join (
select c_provider,c_store_id,count(c_gcode)  count_gcode 
from tb_gdsprovider where c_status_gp='正常进货' group by c_provider,c_store_id 
) gp on p.c_no=gp.c_provider and dg.c_store_id=gp.c_store_id --and dg.c_gcode=gp.c_gcode
where 1=1 
and convert(char(10),dg.c_dt,20)>=@开始时间 and convert(char(10),dg.c_dt,20)<=@结束时间
--and (isnull(@机构,'')='' or dg.c_store_id in (select c_str from  dbo.uf_split_string(isnull(@机构,''),',') ))
and (isnull(@机构,'')='' or dg.c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default) ))
and (isnull(@供应商编码,'')='' or p.c_no=@供应商编码)
and (isnull(@分类,'')='' or dg.c_ccode like @分类+'%')
and dg.c_sale is not null
group by dg.c_store_id,s.c_sname,dg.c_gcode,g.c_name,p.c_no,p.c_name ,dg.c_gcode
order by p.c_no,dg.c_store_id



-- [io]品类动销率T11.2
alter function io_get_salegcodekid(@c_store_id varchar(10),@c_gcode varchar(20),@c_dt datetime)
returns table
as
	return select top 1 c_dt as c_dt_pre,c_store_id,c_gcode,c_number,c_at_cost from tbs_d_gds where c_dt<@c_dt and c_store_id=@c_store_id and c_gcode=@c_gcode order by c_dt desc
sp_helptext 'io_get_gds_gcode_cnt'
-- True  --49	3
  declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime ,@品类层级 int, @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11023',@开始时间='2025-04-28' , @结束时间='2025-04-28',@显示无变动商品='否',@部门='11',@分类='',@商品名称='',@预警天数=3,@销售频率='畅销' ;
--select @品类层级=1 ;
 select gc.c_ccode as 分类号码,gc.c_name as 分类名称 
,count(distinct g.c_gcode) as 单品数
,count(distinct case when isnull(g.c_sale,0)<>0 then g.c_gcode else null end) as 动销数
,round(cast(count(distinct case when isnull(g.c_sale,0)<>0 then g.c_gcode else null end) as dec(12,2))/count(distinct g.c_gcode),4) as 动销率
,count(distinct g.c_gcode)-count(distinct case when isnull(g.c_sale,0)<>0 then g.c_gcode else null end) as 不动销数
from tb_gdsclass  gc
cross apply dbo.io_get_gds_gcode_cnt(@机构,gc.c_ccode,@开始时间,@结束时间) g
--cross apply dbo.io_get_gds_gcode_salecnt(@机构,gc.c_ccode,@开始时间,@结束时间) dg
where 1=1
and (isnull(@品类层级,'')='' or gc.c_level=@品类层级)
and (isnull(@分类,'')='' or gc.c_ccode like @分类+'%')
--and g.c_sale_status not in ('暂停销售')  
--and (   (g.c_number<>0) 
--		or (g.c_number=0 and g.c_sale<>0)
--	)
and g.c_sale_status not in ('暂停销售')
and not (g.c_number=0 and g.c_status  in ('暂停进货') )
and gc.c_ccode not like '44%'
--and gc.c_level=1
--and gc.c_ccode='220010204'
and gc.c_ccode=g.c_ccode_pre 
group by gc.c_ccode,gc.c_name
order by gc.c_ccode

--select * from tb_gdsclass
-- [io]不动销商品明细T11.3
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime ,@品类层级 int, @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11026',@开始时间='2025-07-01' , @供应商编码='',@结束时间='2025-08-08',@部门='',@分类='',@商品名称='',@销售频率='畅销' ;
select @品类层级=null ;
-- select top 100 * from tb_gdsstore
-- select * from dbo.io_get_gds_gcode_cnt(@机构,'333030105',@开始时间,@结束时间) g where c_gcode='010092'
-- select * from tb_gdsprovider where c_gcode='010092'
--商品品名	条码	规格	单位	进价	售价	毛利率	最后一次进货日期	库存数量	备注
select g.c_store_id as 机构,g.c_gcode as 商品编码,g.c_name as 商品名称,g.c_barcode as 商品条码,g.c_adno as 部门, g.c_model as 规格
,g.c_ccode as 商品分类,g.c_basic_unit as 单位,g.c_pt_cost as 进价,g.c_price as 售价,
case when g.c_price=0 then null else (g.c_price-g.c_pt_cost)/g.c_price end as 毛利率,
gp.c_provider as 主供应商, p.c_name as 主供应商名,
g.c_lastin_dt as 最后一次进货日期,g.c_lastsale_dt as 最后销售日期,g.c_number as 库存数量,g.c_sale_status as 销售状态 ,g.c_status as 商品状态
from tb_gdsclass  gc
cross apply dbo.io_get_gds_gcode_cnt(@机构,gc.c_ccode,@开始时间,@结束时间) g
left join tb_gdsprovider gp on gp.c_store_id=g.c_store_id and gp.c_gcode=g.c_gcode and gp.c_status='主供应商'
left join tb_partner p on p.c_no=gp.c_provider 
where 1=1
and isnull(g.c_sale,0) =0 
and (isnull(@部门,'')='' or g.c_adno in (select c_str from dbo.uf_split_string(@部门,',')) )
and (isnull(@分类,'')='' or gc.c_ccode like @分类 + '%') and len(gc.c_ccode)=9
and g.c_sale_status not in ('暂停销售')
and not (g.c_number=0 and g.c_status  in ('暂停进货') )
and gc.c_ccode not like '44%'
and (isnull(@供应商编码,'')='' or p.c_no = @供应商编码)
and g.c_type like '%自营%'
and gc.c_ccode=g.c_ccode_pre 
order by g.c_gcode,gc.c_ccode

select distinct c_sale_status,c_status from tb_gdsstore
-- 目前未有商品品态,用库存状态
-- [io]品态异常T12
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime ,@品类层级 int, @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11021',@开始时间='2025-04-28' , @结束时间='2025-04-28',@显示无变动商品='否',@部门='11',@分类='1',@商品名称='',@预警天数=3,@销售频率='畅销' ;
select @品类层级=1 ;
--品名	条码	规格	单位	新品日	异动日	商品品态	供应商名称	库存数量	日均销售	库存天数	最后收货日期	最后销售日期	分类	供应商
select g.c_name as 品名,g.c_barcode as 条码,g.c_model as 规格,g.c_basic_unit as 单位,gs.c_introduce_date as 新品日,
null as w异动日,gs.c_store_status as w商品品态,gs.c_store_status as 库存状态,
p.c_name as 主供应商名称,gs.c_number as 库存数量,gs.c_sn_perday as 日均销量,gs.c_dnlmt_day as w库存天数,
gs.c_lastin_dt as 最后收货日期,gs.c_lastsale_dt as 最后销售日期,
gc.c_name as 分类名称, gs.c_provider as 主供应商
from tb_gdsstore gs
left join tb_gds g on g.c_gcode=gs.c_gcode
left join tb_gdsclass gc on gc.c_ccode=g.c_ccode 
left join tb_partner p  on p.c_no=gs.c_provider
where  (isnull(@机构,'')='' or gs.c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1 , default ) ))
and gs.c_status not like '作废' and  gs.c_store_status<>'正常商品'


-- 库存天数,滞销天数   无公式 ,未写完
-- [io]滞销商品T13
declare @商品编码 varchar(max),@机构 varchar(1000),@部门 varchar(1000),@分类 varchar(1000),@商品名称 varchar(max),@显示无变动商品 varchar(max),@计算方式 varchar(100),
@开始时间 datetime,@结束时间 datetime, @供应商编码 varchar(max) , @对比开始时间 datetime , @对比结束时间 datetime ,@品类层级 varchar(20), @预警天数 int,@销售频率 varchar(50)
select @商品编码='' , @机构='11021,11026',@开始时间='2025-06-01' , @结束时间='2025-06-15',@显示无变动商品='否',@部门='11',@分类='' ;
select @品类层级='第三层' ,@计算方式='以上全部';    -- 销量6%  , 销额1% , 以上全部

declare @codelen int
select @codelen=codelen from io_ccode where name=@品类层级
print @codelen ;
with temp as (
select  c_store_id,c_gcode,c_ccode,sum(c_number_sale) as c_number_sale,sum(c_sale) as c_sale,
DENSE_RANK() over (partition by c_store_id,substring(c_ccode,1,@codelen) order by sum(c_sale) ) as sortby_sum_sale,
DENSE_RANK() over (partition by c_store_id,substring(c_ccode,1,@codelen) order by sum(c_number_sale) ) as sortby_sum_number,
count(*) over (partition by c_store_id,substring(c_ccode,1,@codelen)) as allcount
from tbs_d_gds
where 1=1 
and convert(char(10),c_dt,20) between @开始时间 and @结束时间
and (isnull(@机构,'')='' or c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default) ))
--and case when @品类层级<=2 then substring(c_ccode,1,@品类层级+1) else substring(c_ccode,1,@品类层级+2) end in (select c_ccode from tb_gdsclass where c_level=@品类层级)
group by c_store_id,c_gcode,c_ccode

), temp01 as(
select c_store_id,c_gcode,c_ccode,c_number_sale,c_sale,
sortby_sum_sale,1.00*sortby_sum_sale/allcount as sortby_sum_sale_percent,
sortby_sum_number,1.00*sortby_sum_number/allcount as sortby_sum_number_percent,
allcount
from temp
),temp02 as (
	select * from temp01 where 1=1
	and (@计算方式='销量6%' or sortby_sum_sale_percent<=0.06)
	and (@计算方式='销额1%' or sortby_sum_number_percent<=0.01)
	and (@计算方式='以上全部' or (sortby_sum_sale_percent<=0.06 and sortby_sum_number_percent<=0.01  ))
)
/*----++++*/

select gs.c_store_id as 机构编码,s.c_name as 机构名称,gs.c_gcode as 商品编码,g.c_name as 商品名称,gs.c_ccode as 品类, 
g.c_barcode as 条码,g.c_model as 规格,gstore.c_introduce_date as 新品日,
gstore.c_status as 商品品态,gstore.c_pro_status as 促销,gstore.c_sale_frequency as 畅销, gstore.c_pt_cost as 进价,
gstore.c_price as 售价, 
case when gstore.c_price=0 then null else (gstore.c_price-gstore.c_pt_cost) / gstore.c_price end as 毛利率,
gstore.c_number as 库存数量,gstore.c_at_cost as 库存成本,
gstore.c_sn_perday as 日均销量,gstore.c_dnlmt_day as 安全库存天数,
case when gstore.c_sn_perday=0 then null else (gstore.c_number / gstore.c_sn_perday)-gstore.c_dnlmt_day  end as 滞销天数,
gstore.c_lastin_dt as 最后收货日期,gstore.c_lastsale_dt as 最后销售日期,gstore.c_adno as 部门,
gc.c_ccode as 分类编码,gc.c_name as 分类名称, p.c_no as 主供应商编码, p.c_name as 主供应商名称,
c_number_sale as 销售数量,c_sale as 销售金额,
sortby_sum_number as 销量排名,sortby_sum_sale as 销额排名 ,
sortby_sum_number_percent as 销量排名率,sortby_sum_sale_percent as 销额排名率
from 
temp02 gs
left join tb_gds g on g.c_gcode=gs.c_gcode
left join tb_gdsstore gstore on gs.c_store_id=gstore.c_store_id and gs.c_gcode=gstore.c_gcode
left join tb_gdsclass gc on gc.c_ccode=g.c_ccode 
left join tb_gdsprovider gp on  gs.c_store_id=gp.c_store_id and gs.c_gcode=gp.c_gcode and  gp.c_status='主供应商'
left join tb_partner p  on p.c_no=gp.c_provider
left join tb_store s on gs.c_store_id=s.c_id
where  (isnull(@机构,'')='' or gs.c_store_id in (select c_str from  dbo.uf_io_split_string( @机构, ',','store',1,default) ))
and (isnull(@供应商编码,'')='' or p.c_no = @供应商编码)
and (isnull(@部门,'')='' or   gstore.c_adno=@部门)
and (isnull(@分类,'')='' or gc.c_ccode like @分类+ '%')
and (gstore.c_number<>0) and gstore.c_adno<>'14'
and (isnull(gstore.c_sn_perday,0)<>0)
order  by gs.c_store_id,substring(gs.c_ccode,1,@codelen)
  
alter FUNCTION io_div (@div1 decimal(10,2)    ,@div2 decimal(10,2)    ,@point‌ int=2)      
RETURNS decimal(10,2)      
AS      
BEGIN      
       
    --RETURN case when @div2=0 then 0 else cast(@div1 as float)/cast(@div2 as float) end;     
 --RETURN case when @div2=0 then 0 else @div1/@div2 end;   
 --return  @div1/@div2 ;  
 --RETURN case when @div2=0 then null else round((cast(@div1 as float)/cast(@div2 as float)),@point‌) end;      
 declare @re decimal(10,2) 
  if @div2=0 
	select @re=null
  else 
	select @re=round((cast(@div1 as float)/cast(@div2 as float)),@point‌)
  return @re
END;


