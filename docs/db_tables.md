# 宜家天润超市数据库表结构说明

> 数据库: enjoy_shq_test | SQL Server

---

## tb_store

**门店信息主表** | 约 26 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_id | varchar | 10 | NO | 单据ID/编号 |
| c_pycode | varchar | 10 | YES | 拼音码 |
| c_type | varchar | 20 | NO | 类型 |
| c_ownership_type | varchar | 20 | NO | 归属类型 |
| c_template_store | varchar | 10 | YES | 模板门店 |
| c_status | varchar | 20 | NO | 状态 |
| c_name | varchar | 40 | NO | 名称 |
| c_sname | varchar | 40 | YES | 简称 |
| c_city | varchar | 20 | YES | 城市 |
| c_address | nvarchar | 100 | YES | 地址 |
| c_postcode | varchar | 10 | YES |  |
| c_tele | varchar | 20 | YES |  |
| c_fax | varchar | 20 | YES |  |
| c_region | varchar | 40 | YES |  |
| c_ip | varchar | 100 | YES |  |
| c_server_name | varchar | 100 | YES |  |
| c_net | varchar | 20 | YES |  |
| c_level | varchar | 20 | YES |  |
| c_price_level | varchar | 10 | YES |  |
| c_area | decimal | - | YES |  |
| c_employee_number | int | - | YES |  |
| c_stock_enlarge | decimal | - | YES |  |
| c_sale_enlarge | decimal | - | YES |  |
| c_open_date | datetime | - | YES |  |
| c_intro | varchar | 1000 | YES |  |
| c_web_page | varchar | 200 | YES |  |
| c_manager_userno | varchar | 10 | YES |  |
| c_manager_mobile | varchar | 20 | YES |  |
| c_modified_dt | datetime | - | YES | 最后修改时间 |
| c_modified_userno | varchar | 10 | YES |  |
| c_reg_code | varchar | 300 | YES |  |
| c_settle_region | varchar | 20 | YES |  |
| c_charger_post | varchar | 36 | YES |  |
| c_booking_order_limit | int | - | YES |  |
| c_tax_regno | varchar | 50 | YES |  |
| c_account_bank | varchar | 40 | YES |  |
| c_account_name | varchar | 60 | YES |  |
| c_account_no | varchar | 80 | YES |  |
| c_class | varchar | 40 | YES |  |
| c_reg_code2 | nvarchar | 300 | YES |  |
| c_run_store_id | varchar | 10 | YES |  |
| c_mprice_type | varchar | 20 | YES |  |
| c_store_guid | varchar | 36 | YES |  |
| c_booking_user | varchar | 100 | YES |  |
| c_booking_tele | varchar | 100 | YES |  |
| c_mother_store_id | varchar | 10 | YES |  |
| c_map_store_id | varchar | 10 | YES |  |
| c_owner | nvarchar | 50 | YES |  |
| c_store_level | nvarchar | 20 | YES |  |
| c_counter_len | float | - | YES |  |
| c_id_level | varchar | 10 | YES |  |
| c_reg_code_mobile | nvarchar | 300 | YES |  |
| c_owner_name | nvarchar | 50 | YES |  |
| c_prefix_Code | varchar | 10 | YES |  |
| c_email | varchar | 100 | YES |  |
| c_close_dt | datetime | - | YES |  |
| c_property | varchar | 500 | YES |  |
| c_cost_center_no | varchar | 20 | YES |  |
| c_organize_no | varchar | 20 | YES |  |
| c_reg_code_pda | nvarchar | 300 | YES |  |
| c_store_extend | nvarchar | - | YES |  |
| c_reg_datacatch | varchar | 100 | YES |  |
| c_store_route_no | varchar | 10 | YES |  |
| c_extend_filed | xml | - | YES |  |
| c_tree_guid | nvarchar | 36 | YES |  |
| c_par_guid | nvarchar | 36 | YES |  |
| c_teminal | nvarchar | 10 | YES |  |

## tb_pos_flow_head

**POS销售流水头表（每笔交易一条记录）** | 约 1,249,107 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_no | varchar | 40 | NO | 单据编号 |
| c_begin_time | datetime | - | YES | 交易开始时间 |
| c_cashier | varchar | 10 | YES | 收银员编号 |
| c_cardno | varchar | 30 | YES | 会员卡号 |
| c_score | decimal | - | NO | 积分 |
| c_pos | int | - | YES | POS机号 |
| c_store_id | varchar | 10 | NO | 门店ID |
| c_type | varchar | 10 | YES | 类型 |
| c_end_time | datetime | - | YES | 交易结束时间 |
| c_amount | decimal | - | YES | 金额 |
| c_pay | decimal | - | YES | 实付金额 |
| c_change | decimal | - | YES | 找零 |
| c_balance | decimal | - | YES | 余额 |
| c_invoice_no | varchar | 250 | YES |  |
| c_source | varchar | 20 | YES | 来源 |
| c_mark | varchar | 40 | YES | 标记/唯一标识 |
| c_status | varchar | 10 | YES | 状态 |
| c_s_flag | int | - | YES |  |
| c_duty | varchar | 10 | YES | 班次 |
| c_identity | int | - | NO | 自增标识 |
| c_mid | varchar | 42 | YES | 介质ID(会员卡) |
| c_sale_time | datetime | - | YES | 销售时间 |
| c_source_no | varchar | 40 | YES |  |
| c_rmis_identity | int | - | NO |  |
| c_pos_prop | varchar | 64 | YES |  |
| c_insert_time | datetime | - | YES | 数据插入时间 |
| c_rmis_insert_dt | datetime | - | YES |  |
| c_pos3_insert_dt | datetime | - | YES |  |
| c_spliting_status | varchar | 20 | YES |  |
| c_weight | decimal | - | YES |  |
| c_FaceID | varchar | 100 | YES |  |
| c_gate_tax | decimal | - | YES | 关税 |
| c_head_note | varchar | 200 | YES |  |
| c_cardname | varchar | 40 | YES | 卡类型名称 |
| c_customer | nvarchar | 50 | YES | 顾客编号/姓名 |
| c_cust_no | varchar | 20 | YES | 顾客编号 |
| c_cust_tele2 | varchar | 50 | YES |  |
| c_out_order_no | varchar | 50 | YES |  |
| c_cust_name | nvarchar | 50 | YES | 顾客姓名 |
| c_sale_channel | varchar | 50 | YES | 销售渠道 |
| c_charger | varchar | 20 | YES | 负责人编号 |
| c_order_type | varchar | 20 | YES |  |
| c_score_flag | int | - | YES |  |

## tb_pos_flow_goods

**POS销售流水商品明细表（每笔交易中的每个商品）** | 约 4,071,712 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_no | varchar | 40 | NO | 单据编号 |
| c_sort | int | - | NO | 序号 |
| c_store_id | varchar | 10 | NO | 门店ID |
| c_pos | int | - | YES | POS机号 |
| c_in_code | varchar | 30 | YES | 录入编码 |
| c_input_type | varchar | 10 | YES |  |
| c_raw | int | - | YES |  |
| c_multiple | decimal | - | YES |  |
| c_barcode | varchar | 20 | YES | 商品条码 |
| c_bar_qty | decimal | - | YES |  |
| c_b_price | decimal | - | YES |  |
| c_b_mprice | decimal | - | YES |  |
| c_b_price_pro | decimal | - | YES |  |
| c_b_mprice_pro | decimal | - | YES |  |
| c_qty_limit | decimal | - | YES |  |
| c_bardisc | decimal | - | YES |  |
| c_gcode | varchar | 16 | YES | 商品编码 |
| c_subcode | varchar | 10 | YES | 商品子码 |
| c_name | varchar | 50 | YES | 名称 |
| c_basic_unit | varchar | 10 | YES | 基本单位 |
| c_model | varchar | 20 | YES | 规格型号 |
| c_adno | varchar | 10 | YES | 区域编号(管理区) |
| c_ccode | varchar | 16 | YES | 分类编码 |
| c_type | varchar | 20 | YES | 类型 |
| c_brand | varchar | 40 | YES | 品牌 |
| c_provider | varchar | 16 | YES | 供应商编码 |
| c_trademark | varchar | 40 | YES | 商标 |
| c_pro_status | varchar | 20 | YES | 促销状态 |
| c_disc_limit | varchar | 260 | YES | 折扣限制 |
| c_pt_cost | decimal | - | YES | 移动平均成本价 |
| c_price | decimal | - | YES | 零售价/单价 |
| c_price_disc | decimal | - | YES | 折扣价 |
| c_mprice | decimal | - | YES |  |
| c_mprice_disc | decimal | - | YES |  |
| c_price_w | decimal | - | YES |  |
| c_price_min | decimal | - | YES | 最低价 |
| c_tax_rate | decimal | - | YES | 税率 |
| c_price_sale | decimal | - | YES |  |
| c_price_sale_disc | decimal | - | YES |  |
| c_qty | decimal | - | YES | 数量 |
| c_qty_disc | decimal | - | YES |  |
| c_qty_sum | decimal | - | YES |  |
| c_amount | decimal | - | YES | 金额 |
| c_score | decimal | - | YES | 积分 |
| c_seller | varchar | 10 | YES | 营业员编号 |
| c_charger | varchar | 10 | YES | 负责人编号 |
| c_score_rule | varchar | 20 | YES |  |
| c_score_use | decimal | - | YES |  |
| c_trace_serial | varchar | 30 | YES |  |
| c_org_no | varchar | 40 | YES |  |
| c_sale_info | varchar | 20 | YES |  |
| c_sale_type | varchar | 20 | YES |  |
| c_reject_reason | varchar | 200 | YES |  |
| c_warehouse | varchar | 20 | YES |  |
| c_invoice_no | varchar | 20 | YES |  |
| c_property | varchar | 40 | YES |  |
| c_sale_time | datetime | - | YES | 销售时间 |
| c_deal_type | varchar | 20 | YES |  |
| c_prepay_card | varchar | 30 | YES |  |
| c_present_name | varchar | 45 | YES | 赠品名称 |
| c_short_name | varchar | 50 | YES | 简称 |
| c_subname | varchar | 20 | YES |  |
| c_sale_status | varchar | 20 | YES | 销售状态 |
| c_note | varchar | 200 | YES |  |
| c_pro_id | varchar | 20 | YES |  |
| c_rmis_insert_dt | datetime | - | YES |  |
| c_pos3_insert_dt | datetime | - | YES |  |
| c_identity | int | - | YES | 自增标识 |
| c_rmis_goods_identity | bigint | - | NO |  |
| c_order_no | varchar | 40 | YES | 订单号 |
| c_weight | decimal | - | YES |  |
| c_pro_status_org | varchar | 20 | YES |  |
| c_gate_tax | decimal | - | YES | 关税 |
| c_gate_tax_rate | decimal | - | YES |  |
| c_approval_price | decimal | - | YES |  |
| c_gate_code | varchar | 50 | YES |  |
| c_property_description | varchar | 120 | YES |  |
| c_pro_mem_id | varchar | 20 | YES |  |
| c_pro_mem_status | varchar | 20 | YES |  |
| c_pro_guid | varchar | 36 | YES |  |
| c_gds_tax_code | varchar | 20 | YES |  |

## tb_pos_flow_pay

**POS销售流水支付明细表（每笔交易的支付方式）** | 约 1,314,772 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_no | varchar | 40 | NO | 单据编号 |
| c_sort | int | - | NO | 序号 |
| c_type | varchar | 40 | YES | 类型 |
| c_cardno | varchar | 50 | YES | 会员卡号 |
| c_cardname | varchar | 40 | YES | 卡类型名称 |
| c_account | varchar | 100 | YES | 账户 |
| c_amount | decimal | - | YES | 金额 |
| c_pay_time | datetime | - | YES | 支付时间 |
| c_pay_serial | varchar | 100 | YES | 支付流水号 |
| c_pay_id | varchar | 100 | YES | 支付ID |
| c_period | int | - | YES |  |
| c_accept_depart | varchar | 30 | YES |  |
| c_publish_depart | varchar | 30 | YES |  |
| c_paid | decimal | - | YES | 实付金额/已付金额 |
| c_rate | decimal | - | YES | 汇率 |
| c_paid_rmb | decimal | - | YES | 人民币实付 |
| c_remain | decimal | - | YES | 余额 |
| c_deduction | decimal | - | YES | 抵扣金额 |
| c_score_factor | decimal | - | YES |  |
| c_print_flag | varchar | 10 | YES |  |
| c_store_id | varchar | 10 | NO | 门店ID |
| c_pos | int | - | YES | POS机号 |
| c_can_cancel | varchar | 10 | YES |  |
| c_can_change | varchar | 10 | YES |  |
| c_change | decimal | - | YES | 找零 |
| c_rmis_insert_dt | datetime | - | YES |  |
| c_pos3_insert_dt | datetime | - | YES |  |
| c_identity | int | - | YES | 自增标识 |
| c_rmis_pay_identity | bigint | - | NO |  |
| c_org_sort | int | - | YES |  |
| c_isInvoice | nvarchar | 10 | YES |  |
| c_pay_note | nvarchar | 100 | YES |  |
| c_deduction2 | money | - | YES |  |
| c_deduction3 | money | - | YES |  |
| c_achieve_orderid | varchar | 200 | YES |  |
| c_orderid | varchar | 50 | YES |  |
| c_cost_amount | money | - | YES |  |
| c_cost_value2 | decimal | - | YES |  |
| c_pay_channel | varchar | 50 | YES |  |
| c_pay_round | money | - | YES |  |
| c_pay_code | varchar | 50 | YES |  |

## tb_gds

**商品主表（商品基本信息）** | 约 98,346 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_guid | varchar | 36 | NO | 全局唯一标识(GUID) |
| c_gcode | varchar | 20 | NO | 商品编码 |
| c_subcode | varchar | 10 | NO | 商品子码 |
| c_barcode | varchar | 20 | YES | 商品条码 |
| c_pycode | varchar | 10 | YES | 拼音码 |
| c_stat_code | varchar | 100 | NO |  |
| c_pluno | varchar | 10 | YES |  |
| c_ccode | varchar | 12 | NO | 分类编码 |
| c_allude_gcode | varchar | 13 | YES |  |
| c_name | varchar | 50 | NO | 名称 |
| c_subname | varchar | 20 | YES |  |
| c_short_name | varchar | 50 | YES | 简称 |
| c_basic_unit | varchar | 10 | YES | 基本单位 |
| c_in_unit | varchar | 10 | YES | 入库单位 |
| c_content | decimal | - | NO | 换算系数 |
| c_distr_content | decimal | - | NO |  |
| c_price | money | - | YES | 零售价/单价 |
| c_price_disc | money | - | YES | 折扣价 |
| c_price_mem | money | - | YES | 会员价 |
| c_price_min | money | - | YES | 最低价 |
| c_price_move | money | - | YES |  |
| c_pt_cost | money | - | YES | 移动平均成本价 |
| c_model | varchar | 20 | YES | 规格型号 |
| c_trademark | varchar | 40 | YES | 商标 |
| c_produce | varchar | 20 | YES |  |
| c_grade | varchar | 10 | YES | 等级 |
| c_quarter | varchar | 12 | YES |  |
| c_label_type | varchar | 10 | YES |  |
| c_tax_rate | decimal | - | YES | 税率 |
| c_type | varchar | 20 | NO | 类型 |
| c_status | varchar | 20 | NO | 状态 |
| c_pro_status | varchar | 20 | NO | 促销状态 |
| c_sale_status | varchar | 20 | NO | 销售状态 |
| c_move_status | varchar | 20 | NO | 调配状态 |
| c_disc_limit | varchar | 255 | YES | 折扣限制 |
| c_present_name | varchar | 40 | YES | 赠品名称 |
| c_cost_method | varchar | 20 | NO | 成本核算方式 |
| c_writeoff_method | varchar | 20 | NO |  |
| c_delivery_type | varchar | 20 | NO | 配送方式(直送/配送) |
| c_order_store_type | varchar | 50 | YES |  |
| c_code_store_id | varchar | 10 | YES |  |
| c_store_id_scope | varchar | 10 | YES |  |
| c_adno | varchar | 10 | NO | 区域编号(管理区) |
| c_ctrlno | varchar | 20 | YES |  |
| c_provider | varchar | 12 | YES | 供应商编码 |
| c_buy_userno | varchar | 10 | YES |  |
| c_au_userno | varchar | 10 | YES |  |
| c_introduce_date | datetime | - | YES | 引进日期 |
| c_rec_date | datetime | - | YES | 收货日期 |
| c_disuse_date | datetime | - | YES | 淘汰日期 |
| c_test_day | int | - | YES |  |
| c_test_plan | decimal | - | YES |  |
| c_od_day | int | - | YES |  |
| c_uplmt_day | int | - | YES |  |
| c_dnlmt_day | int | - | YES |  |
| c_dnlmt_number | int | - | YES |  |
| c_sn_perday | decimal | - | YES | 日均销量 |
| c_sale_frequency | varchar | 20 | YES | 销售频率 |
| c_order_enlarge | decimal | - | YES |  |
| c_depth | decimal | - | YES |  |
| c_width | decimal | - | YES |  |
| c_height | decimal | - | YES |  |
| c_max_layers | int | - | YES |  |
| c_color | int | - | YES |  |
| c_abc | varchar | 10 | YES | ABC分类 |
| c_comment | varchar | 50 | YES |  |
| c_material | nvarchar | 500 | YES |  |
| c_manufacturer | varchar | 100 | YES |  |
| c_manu_address | varchar | 200 | YES |  |
| c_environment | varchar | 200 | YES |  |
| c_eat_method | nvarchar | 500 | YES |  |
| c_web_page | varchar | 200 | YES |  |
| c_intro | varchar | 1000 | YES |  |
| c_picture | nvarchar | 1000 | YES |  |
| c_shelf_picture | nvarchar | 36 | YES |  |
| c_modified_dt | datetime | - | YES | 最后修改时间 |
| c_modified_userno | varchar | 10 | YES |  |
| c_brand | varchar | 40 | YES | 品牌 |
| c_sn_perday_pro | decimal | - | YES |  |
| c_abc_rank | int | - | YES |  |
| c_bay | varchar | 20 | YES |  |
| c_weight | decimal | - | YES |  |
| c_depth_distr | decimal | - | YES |  |
| c_width_distr | decimal | - | YES |  |
| c_height_distr | decimal | - | YES |  |
| c_weight_distr | decimal | - | YES |  |
| c_price_mem_disc | money | - | YES |  |
| c_color_str | varchar | 40 | YES |  |
| c_size | varchar | 50 | YES |  |
| c_No | varchar | 50 | YES |  |
| c_series | varchar | 50 | YES |  |
| c_style | varchar | 50 | YES |  |
| c_first_order_dt | datetime | - | YES |  |
| c_firstsale_dt | datetime | - | YES | 首次销售时间 |
| c_timeliness | varchar | 20 | YES |  |
| c_process_type | varchar | 20 | YES |  |
| c_wprice | money | - | YES |  |
| c_extend | nvarchar | - | YES |  |
| c_qualitycheck_method | nvarchar | 20 | YES |  |
| c_bigness | decimal | - | YES |  |
| c_gds_level | nvarchar | 20 | YES |  |
| c_pallets | decimal | - | YES |  |
| c_third_ccode | varchar | 20 | YES |  |
| c_gds_tax_code | varchar | 20 | YES |  |
| c_u_level | varchar | 10 | YES |  |
| c_measurement_way | varchar | 10 | YES |  |
| c_measurement_type | varchar | 10 | YES |  |
| c_rec_processType | varchar | 10 | YES |  |
| c_txd_xml | xml | - | YES |  |
| c_is_group | nchar | 10 | YES |  |
| c_gdsclass_type | varchar | 20 | YES |  |
| c_extend1 | varchar | 50 | YES |  |
| c_extend2 | varchar | 50 | YES |  |
| c_extend3 | varchar | 50 | YES |  |
| c_extend4 | varchar | 50 | YES |  |
| c_extend5 | varchar | 50 | YES |  |
| c_extend6 | varchar | 50 | YES |  |
| c_extend7 | varchar | 50 | YES |  |
| c_extend8 | varchar | 50 | YES |  |
| c_extend9 | varchar | 50 | YES |  |
| c_extend10 | varchar | 50 | YES |  |

## tb_gdsclass

**商品分类表（层级品类树）** | 约 1,537 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_ccode | varchar | 12 | NO | 分类编码 |
| c_pycode | varchar | 10 | YES | 拼音码 |
| c_name | varchar | 40 | YES | 名称 |
| c_type | varchar | 20 | YES | 类型 |
| c_kind_limit_low | int | - | YES |  |
| c_kind_limit_top | int | - | YES |  |
| c_kind_standard | int | - | YES |  |
| c_profit_limit_low | int | - | YES |  |
| c_profit_limit_top | int | - | YES |  |
| c_profit_standard | int | - | YES |  |
| c_turnover_day_standard | int | - | YES |  |
| c_oos_rate_standard | decimal | - | YES |  |
| c_month_lost_rate_standard | decimal | - | YES |  |
| c_days_sn_perday | int | - | YES |  |
| c_cold_sn_perday | decimal | - | YES |  |
| c_hot_sn_perday | decimal | - | YES |  |
| c_code_hier | varchar | 20 | YES |  |
| c_cost_method | varchar | 20 | YES | 成本核算方式 |
| c_writeoff_method | varchar | 20 | YES |  |
| c_trademark_standard | int | - | YES |  |
| c_pro_percent_standard | decimal | - | YES |  |
| c_high_price | money | - | YES |  |
| c_low_price | money | - | YES |  |
| c_high_price_percent_standard | money | - | YES |  |
| c_low_price_percent_standard | money | - | YES |  |
| c_note | varchar | 1000 | YES |  |
| c_charger | varchar | 20 | YES | 负责人编号 |
| c_dt | datetime | - | YES | 日期/创建时间 |
| c_test_plan_standard | decimal | - | YES |  |
| c_must_cols | varchar | 1000 | YES |  |
| c_min_test_day | int | - | YES |  |
| c_modify_userno | varchar | 10 | YES |  |
| c_wsale_lost_rate | decimal | - | YES |  |
| c_gs_guid | varchar | 36 | YES |  |
| c_gs_status | varchar | 20 | YES |  |
| c_dms_n_min | decimal | - | YES |  |
| c_dms_n_max | decimal | - | YES |  |
| c_min_standard | decimal | - | YES |  |
| c_max_standard | decimal | - | YES |  |
| c_must_produce_dt | varchar | 30 | YES |  |
| c_must_od_day | varchar | 20 | YES |  |
| c_ccode_tax_rate | decimal | - | YES |  |
| c_property_group | varchar | 80 | YES |  |
| c_sn_method | varchar | 20 | YES |  |
| c_shelf_len | money | - | YES |  |
| c_level_h | money | - | YES |  |
| c_level_m | money | - | YES |  |
| c_level_l | money | - | YES |  |
| c_profit_standard_w | decimal | - | YES |  |
| c_fee | money | - | YES |  |
| c_fee_pay_method | varchar | 20 | YES |  |
| c_month_times | decimal | - | NO |  |
| c_level | tinyint | - | YES |  |
| c_id_level | varchar | 50 | YES |  |
| c_code_store_id | varchar | 20 | YES |  |

## tb_gdsstore

**商品-门店库存及价格表** | 约 697,943 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_gcode | varchar | 20 | NO | 商品编码 |
| c_subcode | varchar | 10 | NO | 商品子码 |
| c_adno | varchar | 10 | NO | 区域编号(管理区) |
| c_store_id | varchar | 10 | NO | 门店ID |
| c_price | money | - | YES | 零售价/单价 |
| c_price_disc | money | - | YES | 折扣价 |
| c_price_mem | money | - | YES | 会员价 |
| c_pt_cost | money | - | YES | 移动平均成本价 |
| c_number | decimal | - | YES | 库存数量 |
| c_onway | decimal | - | YES | 在途数量 |
| c_outer | decimal | - | YES | 外借数量 |
| c_to_ret | decimal | - | YES | 待退数量 |
| c_a | money | - | YES | 金额(库存) |
| c_a_cost | money | - | YES | 成本金额 |
| c_at_cost | money | - | YES | 实际成本(含税) |
| c_status | varchar | 20 | NO | 状态 |
| c_pro_status | varchar | 20 | NO | 促销状态 |
| c_sale_status | varchar | 20 | NO | 销售状态 |
| c_move_status | varchar | 20 | NO | 调配状态 |
| c_delivery_type | varchar | 20 | NO | 配送方式(直送/配送) |
| c_disc_limit | varchar | 255 | YES | 折扣限制 |
| c_present_name | varchar | 40 | YES | 赠品名称 |
| c_dnlmt_number | int | - | YES |  |
| c_sn_perday | decimal | - | YES | 日均销量 |
| c_sale_frequency | varchar | 20 | YES | 销售频率 |
| c_rec_date | datetime | - | YES | 收货日期 |
| c_test_day | int | - | YES |  |
| c_test_plan | decimal | - | YES |  |
| c_n_min | decimal | - | YES | 最低库存 |
| c_n_max | decimal | - | YES | 最高库存 |
| c_ctrlno | varchar | 20 | YES |  |
| c_dt | datetime | - | YES | 日期/创建时间 |
| c_sn_perday_pro | decimal | - | YES |  |
| c_firstin_dt | datetime | - | YES | 首次入库时间 |
| c_lastin_dt | datetime | - | YES | 最近入库时间 |
| c_type | varchar | 20 | NO | 类型 |
| c_bay | varchar | 20 | YES |  |
| c_produce | varchar | 20 | YES |  |
| c_od_day | int | - | YES |  |
| c_uplmt_day | int | - | YES |  |
| c_dnlmt_day | int | - | YES |  |
| c_lastsale_dt | datetime | - | YES | 最近销售时间 |
| c_lastin_id | varchar | 20 | YES |  |
| c_provider | varchar | 50 | YES | 供应商编码 |
| c_bad | decimal | - | YES |  |
| c_sample | decimal | - | YES |  |
| c_price_min | money | - | YES | 最低价 |
| c_quarter | varchar | 12 | YES |  |
| c_label_type | varchar | 10 | YES |  |
| c_order_enlarge | decimal | - | YES |  |
| c_content | decimal | - | NO | 换算系数 |
| c_distr_content | decimal | - | NO |  |
| c_abc_rank | int | - | YES |  |
| c_abc | varchar | 10 | YES | ABC分类 |
| c_price_mem_disc | money | - | YES |  |
| c_firstsale_dt | datetime | - | YES | 首次销售时间 |
| c_frozen | decimal | - | YES |  |
| c_nodeliver | decimal | - | YES |  |
| c_comment | varchar | 50 | YES |  |
| c_disuse_date | datetime | - | YES | 淘汰日期 |
| c_first_order_dt | datetime | - | YES |  |
| c_introduce_date | datetime | - | YES | 引进日期 |
| c_tax_rate | decimal | - | YES | 税率 |
| c_guid | varchar | 36 | YES | 全局唯一标识(GUID) |
| c_modified_dt | datetime | - | YES | 最后修改时间 |
| c_wprice | money | - | YES |  |
| c_last_pt_cost | money | - | YES |  |
| c_lastsale_pro_dt | datetime | - | YES |  |
| c_note1 | varchar | 200 | YES |  |
| c_note2 | varchar | 200 | YES |  |
| c_note3 | varchar | 200 | YES |  |
| c_pro_name | varchar | 40 | YES |  |
| c_pro_period | varchar | 20 | YES |  |
| c_wno_limit | varchar | 250 | YES |  |
| c_modified_dt_p | datetime | - | YES |  |
| c_prom_end_dt | datetime | - | YES |  |
| c_store_status | varchar | 20 | YES |  |
| c_serial_no | varchar | 50 | YES |  |
| c_opl_prohibit | varchar | 20 | YES |  |
| c_storage | varchar | 20 | YES |  |
| c_n_min_order | decimal | - | YES |  |
| c_pro_id | varchar | 20 | YES |  |
| c_pp_reason | varchar | 100 | YES |  |
| c_jp_d_price | money | - | YES |  |
| c_d_price | money | - | YES |  |
| c_advice_price | money | - | YES |  |
| c_effective_day | int | - | YES |  |
| c_jp_d_disc_price | money | - | YES |  |
| c_measurement_way | varchar | 10 | YES |  |
| c_measurement_type | varchar | 10 | YES |  |
| c_rec_processType | varchar | 10 | YES |  |
| c_test_dt | datetime | - | YES |  |
| c_et_cost | money | - | YES |  |
| c_property_group | varchar | 80 | YES |  |

## tb_gdsstore_sales

**商品-门店销量汇总表（日/周/月销量、利润）** | 约 733,194 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_store_id | varchar | 20 | NO | 门店ID |
| c_adno | varchar | 20 | NO | 区域编号(管理区) |
| c_gcode | varchar | 13 | NO | 商品编码 |
| c_day1 | decimal | - | NO | 第1天销量 |
| c_day2 | decimal | - | NO | 第2天销量 |
| c_day3 | decimal | - | NO | 第3天销量 |
| c_day4 | decimal | - | NO | 第4天销量 |
| c_day5 | decimal | - | NO | 第5天销量 |
| c_day6 | decimal | - | NO | 第6天销量 |
| c_day7 | decimal | - | NO | 第7天销量 |
| c_week0 | decimal | - | NO | 本周销量 |
| c_week1 | decimal | - | NO | 上周销量 |
| c_week2 | decimal | - | NO | 前2周销量 |
| c_week3 | decimal | - | NO |  |
| c_week4 | decimal | - | NO |  |
| c_month0 | decimal | - | NO | 本月销量 |
| c_month1 | decimal | - | NO | 上月销量 |
| c_month2 | decimal | - | NO | 前2月销量 |
| c_month3 | decimal | - | NO |  |
| c_modify_dt | datetime | - | YES |  |
| c_day1_sale | money | - | NO |  |
| c_day2_sale | money | - | NO |  |
| c_day3_sale | money | - | NO |  |
| c_day4_sale | money | - | NO |  |
| c_day5_sale | money | - | NO |  |
| c_day6_sale | money | - | NO |  |
| c_day7_sale | money | - | NO |  |
| c_week0_sale | money | - | NO |  |
| c_week1_sale | money | - | NO |  |
| c_week2_sale | money | - | NO |  |
| c_week3_sale | money | - | NO |  |
| c_week4_sale | money | - | NO |  |
| c_month0_sale | money | - | NO |  |
| c_month1_sale | money | - | NO |  |
| c_month2_sale | money | - | NO |  |
| c_month3_sale | money | - | NO |  |
| c_day1_profit | money | - | NO |  |
| c_day2_profit | money | - | NO |  |
| c_day3_profit | money | - | NO |  |
| c_day4_profit | money | - | NO |  |
| c_day5_profit | money | - | NO |  |
| c_day6_profit | money | - | NO |  |
| c_day7_profit | money | - | NO |  |
| c_week0_profit | money | - | NO |  |
| c_week1_profit | money | - | NO |  |
| c_week2_profit | money | - | NO |  |
| c_week3_profit | money | - | NO |  |
| c_week4_profit | money | - | NO |  |
| c_month0_profit | money | - | NO |  |
| c_month1_profit | money | - | NO |  |
| c_month2_profit | money | - | NO |  |
| c_month3_profit | money | - | NO |  |
| c_day7_min_price | money | - | YES |  |
| c_day7_max_price | money | - | YES |  |
| c_pro_proid | varchar | 50 | YES |  |
| c_pro_amount | money | - | YES |  |
| c_pro_n | money | - | YES |  |
| c_pro_period | varchar | 20 | YES |  |
| c_pro_at_sale | money | - | YES |  |
| c_pro_period_now | varchar | 20 | YES |  |
| c_pro_proid_now | varchar | 50 | YES |  |
| c_pro_amount_now | money | - | YES |  |
| c_pro_n_now | decimal | - | YES |  |
| c_pro_at_sale_now | money | - | YES |  |
| c_month0_times | decimal | - | NO |  |
| c_month1_times | decimal | - | NO |  |
| c_month2_times | decimal | - | NO |  |
| c_month3_times | decimal | - | NO |  |

## tb_customer

**顾客/会员主表** | 约 167,344 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_no | varchar | 20 | NO | 单据编号 |
| c_name | nvarchar | 50 | YES | 名称 |
| c_id | varchar | 20 | YES | 单据ID/编号 |
| c_type | varchar | 20 | YES | 类型 |
| c_grade | varchar | 20 | YES | 等级 |
| c_group | varchar | 50 | YES |  |
| c_title | varchar | 20 | YES |  |
| c_adress | varchar | 100 | YES | 地址 |
| c_post_code | varchar | 10 | YES |  |
| c_tele1 | varchar | 40 | YES | 电话1 |
| c_tele2 | varchar | 50 | YES | 手机号 |
| c_fax | varchar | 20 | YES |  |
| c_email | varchar | 40 | YES |  |
| c_fond | varchar | 40 | YES |  |
| c_born_date | datetime | - | YES | 出生日期 |
| c_sex | varchar | 2 | YES | 性别 |
| c_earning | varchar | 20 | YES |  |
| c_educattion | varchar | 20 | YES |  |
| c_job | varchar | 20 | YES |  |
| c_score | money | - | YES | 积分 |
| c_used_score | money | - | YES |  |
| c_cut_score | money | - | YES |  |
| c_credit | money | - | YES |  |
| c_dm_status | varchar | 20 | NO |  |
| c_dm_reason | varchar | 50 | YES |  |
| c_p_userno | varchar | 10 | YES |  |
| c_introduce_date | datetime | - | YES | 引进日期 |
| c_mk_store_id | varchar | 10 | YES |  |
| c_store_id | varchar | 10 | YES | 门店ID |
| c_comments | varchar | 50 | YES |  |
| c_note | varchar | 200 | YES |  |
| c_modify_userno | varchar | 10 | YES |  |
| c_modify_dt | datetime | - | YES |  |
| c_sms_status | varchar | 20 | YES |  |
| c_sms_reason | varchar | 50 | YES |  |
| c_join_type | varchar | 50 | YES |  |
| c_corp | varchar | 50 | YES |  |
| c_corp_address | varchar | 50 | YES |  |
| c_corp_tele | varchar | 40 | YES |  |
| c_corp_depart | varchar | 20 | YES |  |
| c_guid | varchar | 36 | YES | 全局唯一标识(GUID) |
| c_note2 | varchar | 200 | YES |  |
| c_note3 | varchar | 200 | YES |  |
| c_hope_prom_action | varchar | 250 | YES |  |
| c_hope_prom_info | varchar | 250 | YES |  |
| c_join_id | varchar | 250 | YES |  |
| c_join_amount | money | - | YES |  |
| c_cust_status | varchar | 20 | YES |  |
| c_s_guid | varchar | 36 | YES |  |
| c_notice_info | nvarchar | 100 | YES |  |
| c_id_type | varchar | 20 | YES |  |
| c_account_no | varchar | 80 | YES |  |
| c_account_bank | nvarchar | 50 | YES |  |
| c_account_name | nvarchar | 60 | YES |  |
| c_valuecard_flag | varchar | 10 | YES |  |
| c_company | nvarchar | 60 | YES |  |
| c_company_address | nvarchar | 100 | YES |  |
| c_category | varchar | 50 | YES |  |
| c_consume_type | nvarchar | 50 | YES |  |
| c_p_userno2 | varchar | 10 | YES |  |
| c_last_score | money | - | YES |  |
| c_last_used_score | money | - | YES |  |
| c_last_cut_score | money | - | YES |  |
| c_last_score_dt | datetime | - | YES |  |
| c_extend | nvarchar | - | YES |  |
| c_cust_comsumed | money | - | YES |  |
| c_last_cust_comsumed | money | - | YES |  |
| c_nation | varchar | 20 | YES |  |
| c_qq | varchar | 50 | YES |  |
| c_msn | varchar | 150 | YES |  |
| c_ecno | varchar | 20 | YES |  |
| c_micromsg_id | nvarchar | 50 | YES |  |
| c_micromsg_dt | datetime | - | YES |  |
| c_first_dt | datetime | - | YES |  |
| c_last_dt | datetime | - | YES |  |
| c_register_channel | varchar | 500 | YES |  |
| c_register_scene | varchar | 500 | YES |  |

## tb_card

**会员卡信息表** | 约 207,109 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_cardno | varchar | 20 | NO | 会员卡号 |
| c_grade | varchar | 10 | NO | 等级 |
| c_cardname | varchar | 40 | NO | 卡类型名称 |
| c_comsumed | money | - | YES | 累计消费 |
| c_paid | money | - | YES | 实付金额/已付金额 |
| c_deposit | money | - | YES | 储值余额 |
| c_type | varchar | 20 | NO | 类型 |
| c_disc_type | varchar | 20 | NO |  |
| c_status | varchar | 20 | NO | 状态 |
| c_mid | varchar | 42 | NO | 介质ID(会员卡) |
| c_s_date | datetime | - | YES |  |
| c_e_date | datetime | - | YES |  |
| c_customer | varchar | 20 | YES | 顾客编号/姓名 |
| c_psword | varchar | 30 | YES |  |
| c_verify | varchar | 30 | YES |  |
| c_mk_store_id | varchar | 10 | YES |  |
| c_store_id | varchar | 250 | YES | 门店ID |
| c_modified_userno | varchar | 10 | YES |  |
| c_modified_dt | datetime | - | YES | 最后修改时间 |
| c_saved | money | - | YES | 已存金额 |
| c_recycle_status | varchar | 20 | YES |  |
| c_recycle_dt | datetime | - | YES |  |
| c_recycle_userno | varchar | 10 | YES |  |
| c_recycle_store_id | varchar | 10 | YES |  |
| c_cardname_new | varchar | 400 | YES |  |
| c_ic_id | varchar | 50 | YES |  |
| c_card_note | varchar | 50 | YES |  |
| c_is_entity | varchar | 10 | YES |  |
| c_bind_psword | varchar | 100 | YES |  |
| c_use_scope | varchar | 100 | YES |  |
| c_is_once | varchar | 10 | YES |  |
| c_card_mk_dt | datetime | - | NO |  |

## tb_o_sg

**销售明细表（商品级）—— 核心销售分析表** | 约 16,005,981 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_guid | varchar | 36 | NO | 全局唯一标识(GUID) |
| c_identity | bigint | - | YES | 自增标识 |
| c_store_id | varchar | 10 | NO | 门店ID |
| c_id | varchar | 40 | NO | 单据ID/编号 |
| c_computer_id | int | - | NO | 电脑/POS编号 |
| c_datetime | datetime | - | NO | 交易日期时间 |
| c_cashier | varchar | 10 | NO | 收银员编号 |
| c_cardno | varchar | 20 | YES | 会员卡号 |
| c_adno | varchar | 10 | NO | 区域编号(管理区) |
| c_gcode | varchar | 13 | NO | 商品编码 |
| c_subcode | varchar | 10 | NO | 商品子码 |
| c_pt_cost | money | - | NO | 移动平均成本价 |
| c_price | money | - | NO | 零售价/单价 |
| c_price_pro | money | - | NO |  |
| c_price_disc | money | - | NO | 折扣价 |
| c_qtty | decimal | - | NO | 数量 |
| c_amount | money | - | NO | 金额 |
| c_deduct_rate | decimal | - | NO | 扣点率 |
| c_score | money | - | NO | 积分 |
| c_gds_type | varchar | 20 | NO | 商品类型(自营/联营) |
| c_pro_status | varchar | 20 | YES | 促销状态 |
| c_present_name | varchar | 40 | YES | 赠品名称 |
| c_type | varchar | 20 | NO | 类型 |
| c_seller | varchar | 10 | YES | 营业员编号 |
| c_charger | varchar | 10 | YES | 负责人编号 |
| c_in_code | varchar | 30 | YES | 录入编码 |
| c_note | varchar | 200 | YES |  |
| c_in_guid | varchar | 36 | YES |  |
| c_price_pro_guid | varchar | 36 | YES |  |
| c_usecard_pro_guid | varchar | 36 | YES |  |
| c_stock_flag | varchar | 20 | YES | 库存标记 |
| c_sg_source | varchar | 20 | YES | 销售来源 |
| c_pro_id | varchar | 20 | YES |  |
| c_tax_rate_sg | decimal | - | YES |  |
| c_serial_no | varchar | 50 | YES |  |
| c_property | varchar | 40 | YES |  |
| c_sale_guid | varchar | 36 | YES | 销售GUID |
| c_gate_tax | decimal | - | YES | 关税 |
| c_at_cost | money | - | YES | 实际成本(含税) |
| c_order_no | varchar | 40 | YES | 订单号 |
| c_duty | varchar | 10 | YES | 班次 |
| c_aet_cost | money | - | YES | 实际成本(不含税) |
| c_sale_channel | varchar | 50 | YES | 销售渠道 |
| c_price_mem | money | - | YES | 会员价 |
| c_cust_no | varchar | 20 | YES | 顾客编号 |
| c_cust_name | nvarchar | 50 | YES | 顾客姓名 |

## tb_o_sm

**销售支付汇总表（支付方式级）** | 约 5,209,745 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_guid | varchar | 36 | NO | 全局唯一标识(GUID) |
| c_identity | int | - | NO | 自增标识 |
| c_store_id | varchar | 10 | NO | 门店ID |
| c_id | varchar | 40 | NO | 单据ID/编号 |
| c_computer_id | int | - | NO | 电脑/POS编号 |
| c_datetime | datetime | - | NO | 交易日期时间 |
| c_cashier | varchar | 10 | NO | 收银员编号 |
| c_cardno | varchar | 50 | YES | 会员卡号 |
| c_amount | money | - | NO | 金额 |
| c_type | varchar | 40 | NO | 类型 |
| c_charger | varchar | 10 | YES | 负责人编号 |
| c_note | varchar | 400 | YES |  |
| c_sm_source | varchar | 20 | YES | 支付来源 |
| c_pay_serial | varchar | 100 | YES | 支付流水号 |
| c_pay_id | varchar | 100 | YES | 支付ID |
| c_cardname | varchar | 40 | YES | 卡类型名称 |
| c_account | varchar | 100 | YES | 账户 |
| c_accept_depart | varchar | 30 | YES |  |
| c_publish_depart | varchar | 30 | YES |  |
| c_duty | varchar | 10 | YES | 班次 |
| c_pay_channel | varchar | 50 | YES |  |

## tbs_d_store

**门店日统计表** | 约 85,715 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_guid | varchar | 36 | NO | 全局唯一标识(GUID) |
| c_store_id | varchar | 10 | NO | 门店ID |
| c_dt | datetime | - | NO | 日期/创建时间 |
| c_type | varchar | 20 | NO | 类型 |
| c_tax_rate | decimal | - | NO | 税率 |
| c_kind | int | - | YES |  |
| c_kind_test | int | - | YES |  |
| c_kind_pro | int | - | YES |  |
| c_kind_ns | int | - | YES |  |
| c_kind_zs | int | - | YES |  |
| c_kind_zs_a | int | - | YES |  |
| c_kind_zs_b | int | - | YES |  |
| c_kind_ss | int | - | YES |  |
| c_kind_ss_hot | int | - | YES |  |
| c_kind_os | int | - | YES |  |
| c_kind_os_cold | int | - | YES |  |
| c_kind_sale | int | - | YES |  |
| c_kind_sale_np | int | - | YES |  |
| c_kind_hot | int | - | YES |  |
| c_kind_cold | int | - | YES |  |
| c_kind_freeze | int | - | YES |  |
| c_number | decimal | - | YES | 库存数量 |
| c_to_ret | decimal | - | YES | 待退数量 |
| c_a | money | - | YES | 金额(库存) |
| c_at_cost | money | - | YES | 实际成本(含税) |
| c_a_cost | money | - | YES | 成本金额 |
| c_number_order | decimal | - | YES |  |
| c_number_rec | decimal | - | YES |  |
| c_a_rec | money | - | YES |  |
| c_at_rec | money | - | YES |  |
| c_number_ret | decimal | - | YES |  |
| c_a_ret | money | - | YES |  |
| c_at_ret | money | - | YES |  |
| c_number_move_in | decimal | - | YES |  |
| c_a_move_in | money | - | YES |  |
| c_at_move_in | money | - | YES |  |
| c_number_move_out | decimal | - | YES |  |
| c_a_move_out | money | - | YES |  |
| c_at_move_out | money | - | YES |  |
| c_number_lost | decimal | - | YES |  |
| c_a_lost | money | - | YES |  |
| c_at_lost | money | - | YES |  |
| c_a_price | money | - | YES |  |
| c_at_price | money | - | YES |  |
| c_number_sale | decimal | - | YES |  |
| c_a_sale | money | - | YES |  |
| c_at_sale | money | - | YES |  |
| c_sale | money | - | YES |  |
| c_sale_pro | money | - | YES |  |
| c_sale_card | money | - | YES |  |
| c_sale_handback | money | - | YES |  |
| c_sale_author | money | - | YES |  |
| c_sale_lost_pro | money | - | YES |  |
| c_sale_lost_card | money | - | YES |  |
| c_sale_lost_handback | money | - | YES |  |
| c_sale_lost_author | money | - | YES |  |
| c_sale_count | int | - | YES |  |
| c_number_use | decimal | - | YES |  |
| c_a_use | money | - | YES |  |
| c_at_use | money | - | YES |  |
| c_number_wholesale | decimal | - | YES |  |
| c_a_wholesale | money | - | YES |  |
| c_at_wholesale | money | - | YES |  |
| c_wholesale | money | - | YES |  |
| c_aet_rec | money | - | YES |  |
| c_aet_ret | money | - | YES |  |
| c_aet_move_in | money | - | YES |  |
| c_aet_move_out | money | - | YES |  |
| c_aet_lost | money | - | YES |  |
| c_aet_price | money | - | YES |  |
| c_aet_sale | money | - | YES |  |
| c_aet_use | money | - | YES |  |
| c_aet_wholesale | money | - | YES |  |
| c_n_onway_move | decimal | - | YES |  |
| c_at_onway_move | money | - | YES |  |
| c_aet_onway_move | money | - | YES |  |

## tb_brand

**品牌表** | 约 6,260 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_guid | varchar | 36 | NO | 全局唯一标识(GUID) |
| c_brand | varchar | 40 | NO | 品牌 |
| c_pycode | varchar | 10 | NO | 拼音码 |
| c_type | varchar | 20 | NO | 类型 |
| c_abc | varchar | 10 | YES | ABC分类 |
| c_manufactory | varchar | 100 | NO |  |
| c_intro | varchar | 1000 | YES |  |
| c_pro_info | varchar | 1000 | YES |  |
| c_web_page | varchar | 200 | YES |  |
| c_note | varchar | 255 | YES |  |
| c_introduce_dt | datetime | - | YES |  |
| c_modified_userno | varchar | 10 | YES |  |
| c_modified_dt | datetime | - | YES | 最后修改时间 |
| c_mk_store_id | varchar | 10 | YES |  |
| c_ccode | varchar | 200 | YES | 分类编码 |
| c_produce | varchar | 200 | YES |  |
| c_style | varchar | 1000 | YES |  |
| c_crowd | varchar | 1000 | YES |  |
| c_price_scope | varchar | 1000 | YES |  |
| c_price_avg | varchar | 50 | YES |  |
| c_store_info | varchar | 200 | YES |  |
| c_linker | varchar | 20 | YES |  |
| c_linker_tele | varchar | 20 | YES |  |
| c_linker_mphone | varchar | 20 | YES |  |
| c_linker_address | varchar | 100 | YES |  |
| c_linker_email | varchar | 50 | YES |  |
| c_cooperation | varchar | 20 | YES |  |
| c_brand_cn | varchar | 40 | YES |  |
| c_brand_en | varchar | 40 | YES |  |
| c_bcode | varchar | 20 | YES |  |
| c_brand_label | varchar | 40 | YES |  |
| c_grade | varchar | 50 | YES | 等级 |
| c_level | varchar | 50 | YES |  |
| c_history | varchar | 1000 | YES |  |
| c_birthland | varchar | 200 | YES |  |
| c_xml_data | varchar | 8000 | YES |  |
| c_status | varchar | 20 | YES | 状态 |
| c_age_scope | varchar | 100 | YES |  |
| c_income_scope | varchar | 100 | YES |  |
| c_property | varchar | 100 | YES |  |
| c_grown_period | varchar | 50 | YES |  |
| c_code_store_id | varchar | 20 | YES |  |

## tb_trademark

**商标/品牌表** | 约 6,260 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_guid | varchar | 36 | NO | 全局唯一标识(GUID) |
| c_tcode | varchar | 10 | NO |  |
| c_name | varchar | 40 | NO | 名称 |
| c_pycode | varchar | 10 | NO | 拼音码 |
| c_type | varchar | 20 | NO | 类型 |
| c_abc | char | 1 | NO | ABC分类 |
| c_manufactory | varchar | 100 | NO |  |
| c_intro | varchar | 1000 | YES |  |
| c_pro_info | varchar | 1000 | YES |  |
| c_web_page | varchar | 200 | YES |  |
| c_note | varchar | 255 | YES |  |
| c_introduce_dt | datetime | - | YES |  |
| c_modified_userno | varchar | 10 | YES |  |
| c_modified_dt | datetime | - | YES | 最后修改时间 |
| c_tname | varchar | 40 | YES |  |
| c_ccode | varchar | 200 | YES | 分类编码 |
| c_mk_store_id | varchar | 10 | YES |  |

## tb_gdsprovider

**商品-供应商关系表** | 约 656,585 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_gcode | varchar | 20 | NO | 商品编码 |
| c_con_no | varchar | 20 | NO |  |
| c_provider | varchar | 10 | NO | 供应商编码 |
| c_fee | money | - | YES |  |
| c_pt_in | money | - | YES |  |
| c_tax_rate_pay | decimal | - | YES |  |
| c_pt_pay | money | - | YES |  |
| c_prom_pt_in | money | - | YES |  |
| c_prom_pt_pay | money | - | YES |  |
| c_prom_deduct_rate | decimal | - | YES |  |
| c_prom_en_dt | datetime | - | YES |  |
| c_deduct_rate | decimal | - | YES | 扣点率 |
| c_min_order_n | decimal | - | YES |  |
| c_init_disc | decimal | - | YES |  |
| c_init_qtty | decimal | - | YES |  |
| c_status | varchar | 20 | YES | 状态 |
| c_pro_status | varchar | 20 | YES | 促销状态 |
| c_buy_n | decimal | - | YES |  |
| c_last_pt_in | money | - | YES |  |
| c_min_pt_in | money | - | YES |  |
| c_max_pt_in | money | - | YES |  |
| c_ave_pt_in | money | - | YES |  |
| c_lastin_dt | datetime | - | YES | 最近入库时间 |
| c_buyer_no | varchar | 10 | YES |  |
| c_introduce_dt | datetime | - | YES |  |
| c_disuse_dt | datetime | - | YES |  |
| c_note | varchar | 255 | YES |  |
| c_modified_dt | datetime | - | YES | 最后修改时间 |
| c_modified_userno | varchar | 10 | YES |  |
| c_store_id | varchar | 10 | NO | 门店ID |
| c_can_return | varchar | 2 | YES |  |
| c_mk_store_id | varchar | 10 | YES |  |
| c_guid | varchar | 36 | YES | 全局唯一标识(GUID) |
| c_pro_name | varchar | 40 | YES |  |
| c_pro_period | varchar | 20 | YES |  |
| c_firstorder_dt | datetime | - | YES |  |
| c_lastorder_dt | datetime | - | YES |  |
| c_d_type | varchar | 20 | NO |  |
| c_s_mode | varchar | 20 | NO |  |
| c_disc_limit_pt | nvarchar | 1000 | YES |  |
| c_dc_store_id | varchar | 10 | NO |  |
| c_dc_site | varchar | 20 | NO |  |
| c_dc_site_ret | varchar | 20 | NO |  |
| c_status_gp | varchar | 20 | YES |  |
| c_prom_id | varchar | 20 | YES |  |

## tb_barcode

**条码表** | 约 108,340 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_barcode | varchar | 20 | NO | 商品条码 |
| c_gcode | varchar | 20 | NO | 商品编码 |
| c_subcode | varchar | 10 | NO | 商品子码 |
| c_n | decimal | - | NO |  |
| c_bardisc | decimal | - | NO |  |
| c_code_store_id | varchar | 10 | NO |  |
| c_remark | varchar | 20 | YES |  |
| c_modified_userno | varchar | 10 | YES |  |
| c_modified_dt | datetime | - | YES | 最后修改时间 |
| c_guid | varchar | 36 | YES | 全局唯一标识(GUID) |
| c_b_price | money | - | YES |  |
| c_b_mprice | money | - | YES |  |
| c_print_qtty | int | - | YES |  |
| c_b_model | varchar | 20 | YES |  |
| c_b_unit | varchar | 10 | YES |  |
| c_b_price_pro | money | - | YES |  |
| c_b_mprice_pro | money | - | YES |  |
| c_p_sdt | datetime | - | YES |  |
| c_p_edt | datetime | - | YES |  |
| c_b_pro_status | nvarchar | 20 | YES |  |
| c_b_weight | decimal | - | YES |  |
| c_barcode_index | varchar | 20 | NO |  |
| c_property_description | varchar | 120 | YES |  |

## tb_contract

**合同表** | 约 956 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_guid | varchar | 50 | NO | 全局唯一标识(GUID) |
| c_con_no | varchar | 20 | NO |  |
| c_provider | varchar | 10 | NO | 供应商编码 |
| c_adno | varchar | 10 | YES | 区域编号(管理区) |
| c_store_id | varchar | - | YES | 门店ID |
| c_st_dt | datetime | - | NO |  |
| c_en_dt | datetime | - | NO |  |
| c_sign_dt | datetime | - | YES |  |
| c_status | varchar | 20 | NO | 状态 |
| c_pay_status | varchar | 20 | NO |  |
| c_continue_con_no | varchar | 20 | YES |  |
| c_pay_type | varchar | 20 | YES |  |
| c_pay_day | int | - | YES |  |
| c_pay_cycle | varchar | 20 | YES |  |
| c_foregift | money | - | YES |  |
| c_deduct_rate | decimal | - | YES | 扣点率 |
| c_can_return | varchar | 2 | YES |  |
| c_kind_limit_top | int | - | YES |  |
| c_last_dt | datetime | - | YES |  |
| c_at_in_out_not_selected | money | - | YES |  |
| c_incharge_userno | varchar | 10 | YES |  |
| c_mk_store_id | varchar | 10 | NO |  |
| c_template | varchar | 100 | YES |  |
| c_note | varchar | 1000 | YES |  |
| c_postpone_method | varchar | 20 | YES |  |
| c_modified_dt | datetime | - | YES | 最后修改时间 |
| c_modified_userno | varchar | 10 | YES |  |
| c_trademark | varchar | 40 | YES | 商标 |
| c_description | varchar | 40 | YES |  |
| c_ccode | varchar | - | YES | 分类编码 |
| c_lock_status | varchar | 20 | YES |  |
| c_day_type | varchar | 20 | NO |  |
| c_region_type | varchar | 20 | YES |  |
| c_counter_no | varchar | 40 | YES |  |
| c_counter_name | varchar | 60 | YES |  |
| c_invalid_dt | datetime | - | YES |  |
| c_complete | varchar | 60 | YES |  |
| c_recbill_Stock_rate | decimal | - | YES |  |
| c_pro_fall_type | varchar | 20 | YES |  |
| c_pay_delay_days | int | - | YES |  |
| c_take_last_dt | datetime | - | YES |  |
| c_id_process | varchar | 20 | YES |  |
| c_cash_center | varchar | 10 | YES |  |
| c_deduct_rate_min | decimal | - | YES |  |
| c_comein_dt | datetime | - | YES |  |
| c_chgpt_fall_type | varchar | 20 | YES |  |
| c_manager | varchar | 20 | YES |  |
| c_pay_cycle_n | int | - | YES |  |
| c_con_main | varchar | 100 | YES |  |
| c_con_min_order | money | - | YES |  |
| c_con_min_order_pack | int | - | YES |  |
| c_con_tax_rate_pay | decimal | - | YES |  |
| c_monthday | varchar | 100 | YES |  |
| c_opl | varchar | 10 | YES |  |
| c_credit_center | varchar | 10 | YES |  |
| c_pos_type | varchar | 20 | YES |  |
| c_print_status | varchar | 50 | YES |  |
| c_print_userno | varchar | 20 | YES |  |
| c_print_dt | datetime | - | YES |  |
| c_print_count | int | - | YES |  |
| c_shipping_method | nvarchar | 20 | YES |  |
| c_s_type | varchar | 20 | YES |  |
| c_effect_dt | datetime | - | YES |  |
| c_old_con_no | varchar | 200 | YES |  |
| c_bottom_base | varchar | 50 | YES |  |
| c_con_no_txt | varchar | 20 | YES |  |
| c_is_mall | bit | - | YES |  |
| c_business_type | nvarchar | 50 | YES |  |
| c_electric_sign | varchar | 10 | NO |  |
| c_electric_type | varchar | 50 | NO |  |

## tb_hr_user

**员工/用户表** | 约 480 行

| 字段名 | 类型 | 长度 | 可空 | 说明 |
|--------|------|------|------|------|
| c_guid | nvarchar | 50 | NO | 全局唯一标识(GUID) |
| c_no | nvarchar | 10 | NO | 单据编号 |
| c_name | nvarchar | 50 | YES | 名称 |
| c_sex | nvarchar | 10 | YES | 性别 |
| c_nation | nvarchar | 100 | YES |  |
| c_education | nvarchar | 20 | YES |  |
| c_marry | nvarchar | 10 | YES |  |
| c_birthday | datetime | - | YES |  |
| c_address | nvarchar | 200 | YES | 地址 |
| c_tele | nvarchar | 20 | YES |  |
| c_special | nvarchar | 20 | YES |  |
| c_school | nvarchar | 100 | YES |  |
| c_id | nvarchar | 20 | YES | 单据ID/编号 |
| c_earning | nvarchar | 20 | YES |  |
| c_email | nvarchar | 50 | YES |  |
| c_work_date | datetime | - | YES |  |
| c_class | nvarchar | 20 | YES |  |
| c_quality | nvarchar | 16 | YES |  |
| c_party | nvarchar | 16 | YES |  |
| c_level | nvarchar | 32 | YES |  |
| c_resident | nvarchar | 64 | YES |  |
| c_account | nvarchar | 32 | YES | 账户 |
| c_depart | nvarchar | 20 | YES |  |
| c_psword | nvarchar | 24 | YES |  |
| c_status | nvarchar | 20 | YES | 状态 |
| c_gz_flag | nvarchar | 10 | YES |  |
| c_depart_sort | nvarchar | 5 | YES |  |
| c_user_sort | nvarchar | 5 | YES |  |
| c_height | int | - | YES |  |
| c_weight | int | - | YES |  |
| c_blood | nvarchar | 10 | YES |  |
| c_left_eye | nvarchar | 10 | YES |  |
| c_right_eye | nvarchar | 10 | YES |  |
| c_strong | nvarchar | 50 | YES |  |
| c_like | nvarchar | 50 | YES |  |
| c_title | nvarchar | 20 | YES |  |
| c_native | nvarchar | 20 | YES |  |
| c_english_level | nvarchar | 20 | YES |  |
| c_computer_level | nvarchar | 20 | YES |  |
| c_health | nvarchar | 50 | YES |  |
| c_store_id | nvarchar | 20 | YES | 门店ID |
| c_recognizor | nvarchar | 20 | YES |  |
| c_recognizor_id | nvarchar | 20 | YES |  |
| c_recognizor_tele | nvarchar | 20 | YES |  |
| c_recognizor_address | nvarchar | 200 | YES |  |
| c_recognizor_depart | nvarchar | 50 | YES |  |
| c_pycode | nvarchar | 10 | YES | 拼音码 |
| c_in_dt | datetime | - | YES |  |
| c_home_tele | nvarchar | 20 | YES |  |
| c_mobile_tele | nvarchar | 20 | YES |  |
| c_account2 | nvarchar | 50 | YES |  |
| c_account3 | nvarchar | 50 | YES |  |
| c_health_id | nvarchar | 50 | YES |  |
| c_health_end_dt | datetime | - | YES |  |
| c_modify_dt | datetime | - | YES |  |
| c_modify_userno | nvarchar | 10 | YES |  |
| c_if_recognize | nvarchar | 10 | NO |  |
| c_if_contract | nvarchar | 10 | NO |  |
| c_urgency_linkman | nvarchar | 50 | YES |  |
| c_urgency_tele | nvarchar | 20 | YES |  |
| c_if_subsidy | nvarchar | 10 | NO |  |
| c_if_examine | nvarchar | 10 | NO |  |
| c_post_salary_status | nvarchar | 20 | YES |  |
| c_note1 | nvarchar | 50 | YES |  |
| c_note2 | nvarchar | 50 | YES |  |
| c_note3 | nvarchar | 50 | YES |  |
| c_appoint_dt | datetime | - | YES |  |
| c_if_checkWork | nvarchar | 10 | NO |  |
| c_checkwork_cardno | nvarchar | 50 | YES |  |
| c_first_contract_dt | datetime | - | YES |  |
| c_bear | nvarchar | 10 | YES |  |
| c_examine_method | nvarchar | 20 | YES |  |
| c_work_card | nvarchar | 10 | YES |  |
| c_noviciate_sdt | datetime | - | YES |  |
| c_noviciate_edt | datetime | - | YES |  |
| c_resident_type | nvarchar | 20 | YES |  |
| c_mk_store_id | nvarchar | 10 | YES |  |
| c_is_dispatch | nvarchar | 10 | YES |  |
| c_flag | nvarchar | 10 | YES |  |
| c_use_ad | varchar | 50 | YES |  |
| c_insure_account_no | nvarchar | 100 | YES |  |
| c_insure_status | nvarchar | 20 | YES |  |
| c_salary_level | nvarchar | 20 | YES |  |
| c_salary_title | nvarchar | 20 | YES |  |
| c_login_code | nvarchar | 100 | YES |  |
| c_account_bank | nvarchar | 50 | YES |  |

