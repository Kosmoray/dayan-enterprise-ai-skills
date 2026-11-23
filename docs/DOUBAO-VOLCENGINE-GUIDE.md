# 豆包工作、扣子与火山方舟接入指南

成都大衍千机科技有限公司开源提供 168 个企业 AI 技能。通过下方目录查看用途和输入要求。

## 豆包工作

打开[豆包工作技能管理](https://www.doubao.com/chat/skills)，在技能上传入口选择单个技能 ZIP。
[v1.6.0 发布页](https://github.com/Kosmoray/dayan-enterprise-ai-skills/releases/tag/v1.6.0)提供船舶修造、半导体耗材两组共 12 个新增技能的导入包。
下载后解压外层文件，再按需选取单个技能 ZIP。上传及启用状态以客户端显示为准。
上一版的完整导入包保存在 [v1.5.0 发布页](https://github.com/Kosmoray/dayan-enterprise-ai-skills/releases/tag/v1.5.0)。

## 扣子与火山方舟

根据当前项目支持的配置方式，选取技能目录内的 `SKILL.md`，把其中的输入约定、执行步骤和检查点放入工作流的相应节点。先用脱敏样本核对输出，再接入业务数据。

## 技能目录

| 技能 | 用途 |
| --- | --- |
| [`dayan-aero-airgap-llm-sizer`](../skills/dayan-aero-airgap-llm-sizer/SKILL.md) | 涉密厂区绝对不能连公网API，但硬件商忽悠你买百万级算力柜！算清32B/70B模型权重、并发KV缓存显存、机房空调改造与三年真实TCO。 |
| [`dayan-aero-fai-inspection`](../skills/dayan-aero-fai-inspection/SKILL.md) | 航材首件包动辄两三百个气泡号，人工抄三坐标报告漏一个形位公差或基准面符号就被主机厂整包退回！逐项交叉校对AS9102/GJB首件三表。 |
| [`dayan-aero-gjb9001-audit`](../skills/dayan-aero-gjb9001-audit/SKILL.md) | 二方审核与军代室检查开出不符合项，车间只会写“员工粗心、加强培训”被直接打回！用五步归因穿透技术状态与防呆工装真因。 |
| [`dayan-aero-lowvol-pmc-kit`](../skills/dayan-aero-lowvol-pmc-kit/SKILL.md) | 军品科研试制一次只投5件却有18道工序，研究所一个急单插进来全车间乱套！算清五轴换装损耗、外协排队周期与装机齐套最晚节点。 |
| [`dayan-aero-special-process-vendor`](../skills/dayan-aero-special-process-vendor/SKILL.md) | 机加工辛辛苦苦干半个月，外协热处理厂Nadcap或特种证书过期3天导致整批航材报废！建立外协特种资质效期与炉温报告逐批防呆卡。 |
| [`dayan-aero-trial-contract-guard`](../skills/dayan-aero-trial-contract-guard/SKILL.md) | 上游边改图纸边催货，最后却按原交期扣你逾期违约金、审价还倒扣差价！重点排雷技术状态变更顺延、暂定价审价封顶与工装产权。 |
| [`dayan-aesthetic-card-depletion`](../skills/dayan-aesthetic-card-depletion/SKILL.md) | 盘点机构预收未耗卡负债池，按45天/90天/180天停滞分层识别退卡高危VIP，生成有专业温度的唤醒复诊方案。 |
| [`dayan-aesthetic-device-nmpa`](../skills/dayan-aesthetic-device-nmpa/SKILL.md) | 核查光电设备与注射耗材NMPA三类医疗器械注册证适用范围，并拉平多级代理商阶梯返利、院端装机分成与防窜货台账。 |
| [`dayan-agri-food-trace-spec`](../skills/dayan-agri-food-trace-spec/SKILL.md) | 好特产好食材别只会在农产品批发市场拼低价！针对中秋年货企业福利团购、商超定制与工会集采，一键生成高溢价企采分级礼盒方案。 |
| [`dayan-ai-bible-ae86`](../skills/dayan-ai-bible-ae86/SKILL.md) | 完整公开成都大衍千机科技内部压箱底的《AI方法论圣经25律》与《AE86大模型物理上限工作线》，帮团队建立不踩坑的企业级AI工程纪律。 |
| [`dayan-ai-data-security-policy`](../skills/dayan-ai-data-security-policy/SKILL.md) | 员工偷偷把未公开报价单、买方清单和核心源码贴进免费公网AI怎么办？一键生成一页纸能落地的《企业AI安全使用分级制度与脱敏规范》。 |
| [`dayan-ai-seminar-anti-scam`](../skills/dayan-ai-seminar-anti-scam/SKILL.md) | 在企业采购外部AI商业课程、获客软件或代运营服务前，协助逐项核对适用条件、交付物明细与阶段协作边界。 |
| [`dayan-ar-collection-escalator`](../skills/dayan-ar-collection-escalator/SKILL.md) | 专治客户拖欠尾款又怕撕破脸丢单！按逾期天数与客户合作价值输出四级递进催收微信话术、正式对账催款函及以货抵债/分期协议要点。 |
| [`dayan-b2b-export-inquiry-quoter`](../skills/dayan-b2b-export-inquiry-quoter/SKILL.md) | 快速梳理海外买家英文询盘邮件与技术规格要求，列出已明确参数、待澄清工况条件与阶梯报价核对要点。 |
| [`dayan-bid-scoring-loop`](../skills/dayan-bid-scoring-loop/SKILL.md) | 解析招标评分点与废标红线，采用写手生成与只读评审专家独立打分找扣分项的多轮收敛闭环，把技术标打磨到高水准。 |
| [`dayan-business-html`](../skills/dayan-business-html/SKILL.md) | 将长篇分析、阶段总结、商业方案或投研报告一键编译成深蓝印刷感、自带KPI卡片与响应式排版的单文件HTML高管汇报页。 |
| [`dayan-cashflow-13week-radar`](../skills/dayan-cashflow-13week-radar/SKILL.md) | 告别账面有利润、账上没钱发工资！按经营流入、刚性兑付、弹性支出与极端回款延迟三档情景测算企业13周现金安全垫。 |
| [`dayan-ceo-ai-morning-brief`](../skills/dayan-ceo-ai-morning-brief/SKILL.md) | 拒绝每天早上被几十个微信群和海量行业噪音淹没！把内部昨日关键经营异动与外部竞品/大宗原材料/政策真信号压成3分钟可读拍板晨报。 |
| [`dayan-chain-store-geo-auditor`](../skills/dayan-chain-store-geo-auditor/SKILL.md) | 面向建材家居、零售餐饮与本地服务连锁品牌，逐店梳理地址门牌、营业状态、服务范围与联系电话的公开准确度。 |
| [`dayan-chengdu-ai-vendor-selector`](../skills/dayan-chengdu-ai-vendor-selector/SKILL.md) | 协助企业分清工业视觉、标准客服SaaS、算力底座、通用考证培训与FDE全案共创五类服务方向，匹配合适合作伙伴。 |
| [`dayan-cis-asis-warranty-contract`](../skills/dayan-cis-asis-warranty-contract/SKILL.md) | 二手挖机和电车卖到零下30度的西伯利亚或哈萨克，买家暴力施工干爆液压泵或续航缩水，反过来拿国内质保法找你索赔几十万！ |
| [`dayan-cis-dealer-spec-sync`](../skills/dayan-cis-dealer-spec-sync/SKILL.md) | 业务员用机翻把“增程式混动”翻成纯电、把“两驱”写成四驱发到俄语Telegram频道，既丢尽专业脸面又引发海关编码错报退单！ |
| [`dayan-cis-ev-battery-dg`](../skills/dayan-cis-ev-battery-dg/SKILL.md) | 两台二手新能源车装进集装箱拉到港口或铁路港，因拿不出UN38.3试验概要、SOC电量超标或把事故泡水车塞进柜子被重罚扣箱！ |
| [`dayan-cis-fx-payment-guard`](../skills/dayan-cis-fx-payment-guard/SKILL.md) | 车已经发过霍尔果斯换完轨，海外买家说卢布坚戈大跌付不出尾款求先放车卖了再给钱！守死“不见全款绝不改电放SMGS收货人”铁律。 |
| [`dayan-cis-vehicle-rfq-quoter`](../skills/dayan-cis-vehicle-rfq-quoter/SKILL.md) | 哈萨克和俄罗斯车商发来一串俄语配置简写问CIP阿拉木图到岸价，漏算双清关务、笼车板费、车管转籍与口岸换装费直接把利润赔光！ |
| [`dayan-cis-vin-smgs-checker`](../skills/dayan-cis-vin-smgs-checker/SKILL.md) | 一列发往阿拉木图和莫斯科的车柜，就因为SMGS运单把车架号X敲成0、毛重跟装箱单差了80公斤，整柜卡在霍尔果斯滞留半个月亏掉几万块！ |
| [`dayan-client-ai-salon-planner`](../skills/dayan-client-ai-salon-planner/SKILL.md) | 协助链主企业、产业园区、商协会与B2B机构策划贴近业务实际的AI主题分享活动，兼顾专业深度与现场互动体验。 |
| [`dayan-clinic-dental-retention`](../skills/dayan-clinic-dental-retention/SKILL.md) | 获客投流贵如金，客户到店一次就流失等于白干！梳理留资预约到店率、面诊咨询卡点、术后康养随访SOP与合规口碑转介绍链路。 |
| [`dayan-clinic-local-geo-rank`](../skills/dayan-clinic-local-geo-rank/SKILL.md) | 模拟本地顾客在豆包、元宝、小红书AI搜附近靠谱种牙、正畸、皮肤科时的真实提问，定位门店资质与价格信息缺口。 |
| [`dayan-cma-gov-tender-composer`](../skills/dayan-cma-gov-tender-composer/SKILL.md) | 针对政府食品抽检、环境监测与环保管家招标文件，逐行锁定CMA附表证明、仪器发票、采样车与项目负责人社保证明。 |
| [`dayan-cma-raw-report-crosscheck`](../skills/dayan-cma-raw-report-crosscheck/SKILL.md) | 在授权签字人签发检测报告前，逐项核对采样单、仪器谱图原始记录、检出限修约与现行判定标准号是否100%吻合。 |
| [`dayan-cma-scope-stamp-guard`](../skills/dayan-cma-scope-stamp-guard/SKILL.md) | 在检测合同评审与报告盖CMA章前，逐参数比对本机构获批资质认定附表（方法号+基质类别），杜绝超范围出证。 |
| [`dayan-code-adversary`](../skills/dayan-code-adversary/SKILL.md) | 打破写完代码自我感觉良好的同温层！在只读隔离态下用生产破坏者、半年后新人与安全戍边三副反方眼镜穿透PR与代码变更，输出阻断级证据链。 |
| [`dayan-cold-chain-batch-margin`](../skills/dayan-cold-chain-batch-margin/SKILL.md) | 综合批次进价、运输分拣费、可售期损耗、冷库仓储周转与渠道扣点，核算不同货源批次的真实净贡献。 |
| [`dayan-construction-claim-audit`](../skills/dayan-construction-claim-audit/SKILL.md) | 干工程最怕活干完了结算被审掉一层皮！对照施工合同与图纸变更记录，梳理设计变更、甲方原因窝工签证证据链及审计核减应对口径。 |
| [`dayan-content-radar`](../skills/dayan-content-radar/SKILL.md) | 从目标买方真实痛点、搜索意图与竞品内容缺口切入，筛出高转化商业选题，直接产出带锋利判断、证据锚点与传播钩子的文章大纲及成稿。 |
| [`dayan-contract-4way-audit`](../skills/dayan-contract-4way-audit/SKILL.md) | 从项目交付、财务现金流、法务合规与销售成交四个独立视角并行拆解合同草案或报价单，输出绿黄红黑四级结论与逐句修改建议。 |
| [`dayan-copywriting-pro`](../skills/dayan-copywriting-pro/SKILL.md) | 把自嗨的技术参数与空洞口号翻译成买单老板一眼看懂的经营账，生成首屏价值主张、痛点共鸣、证据链与低摩擦CTA六段式高转化页面文案。 |
| [`dayan-dental-implant-ortho-sop`](../skills/dayan-dental-implant-ortho-sop/SKILL.md) | 从金牌现场咨询师录音与接诊案例中，提炼不逼单、重医患信任的口腔CBCT看片沟通、集采价格解释与家庭转介绍SOP。 |
| [`dayan-dify-coze-troubleshooter`](../skills/dayan-dify-coze-troubleshooter/SKILL.md) | Demo跑得欢、一上真实业务就超时报错吐乱码！系统排查Dify/Coze长工作流JSON解析崩溃、知识库召回偏题、并发限流与生产落地加固项。 |
| [`dayan-dlab-clinic-privacy-hipaa`](../skills/dayan-dlab-clinic-privacy-hipaa/SKILL.md) | 欧美大技工所和DSO集团审厂第一问：患者口扫照片、CT和真实姓名直接发进微信群或国内网盘？违反美国HIPAA和欧盟GDPR面临天价罚单直接出局！ |
| [`dayan-dlab-crossborder-tat-sla`](../skills/dayan-dlab-crossborder-tat-sla/SKILL.md) | 患者下周三下午2点已经约好躺在伦敦牙椅上戴牙，你的包裹周三下午4点才送到技工所：错过预约直接导致整单拒付并丢掉合作客户！ |
| [`dayan-dlab-mdr-fda-custom-doc`](../skills/dayan-dlab-mdr-fda-custom-doc/SKILL.md) | 发往法兰克福和纽约的义齿快件在海关被FDA或欧盟药监抽检扣货：缺MDR附录XIII定制器械声明、或拿别人的FDA注册号借壳闯关被列入进口黑名单！ |
| [`dayan-dlab-overseas-prospecting`](../skills/dayan-dlab-overseas-prospecting/SKILL.md) | 欧美本土牙科技师老龄化断代、时薪飙破$45且招不到人！别去骚扰牙医诊所，直接切缺人手的中小Dental-Lab老板，用5颗免费精修全锆冠打开年单几十万美金稳定复购！ |
| [`dayan-dlab-stl-rx-triage`](../skills/dayan-dlab-stl-rx-triage/SKILL.md) | 牙医口扫数据肩台全是唾液血渍伪影、颌间距离不足1毫米，审单员没拦住直接上五轴切削烧结，寄到伦敦戴不进去整单免费重做倒赔双程DHL运费！ |
| [`dayan-dlab-zirconia-remake-cost`](../skills/dayan-dlab-zirconia-remake-cost/SKILL.md) | 看似跨国净利率近19%，但一单免费重做(Remake)不仅白搭瓷块人工，还要倒贴一趟$28国际快递费，返修率一旦突破6%利润直接腰斩！ |
| [`dayan-ecommerce-roi-teardown`](../skills/dayan-ecommerce-roi-teardown/SKILL.md) | GMV几百万一看净利倒亏！穿透千川/直通车投流费、退货率、达人佣金与平台扣点算清真实净ROI，并从百条差评挖出改款与详情页命门。 |
| [`dayan-edu-institution-renewal`](../skills/dayan-edu-institution-renewal/SKILL.md) | 消课慢、续费难、老师不会做服务外化！把枯燥课堂表现转化为家长/企业HR看得见的成长证据卡、阶段复盘报告与自然续报沟通剧本。 |
| [`dayan-enterprise-ai-triage`](../skills/dayan-enterprise-ai-triage/SKILL.md) | 协助企业经营者盘点拟推进的AI场景，优先识别高确定性业务切口，梳理数据条件、人工复核边界与30天试点安排。 |
| [`dayan-env-discharge-permit-log`](../skills/dayan-env-discharge-permit-log/SKILL.md) | 对照企业排污许可证副本要求，逐排放口核查自行监测因子、频次漏测、执行管理报告逾期与危废联单台账漏洞。 |
| [`dayan-env-wastewater-cod-triage`](../skills/dayan-env-wastewater-cod-triage/SKILL.md) | 针对食品、化工、印染园区污水站出水COD、氨氮、总磷突发飙升，按进水冲击、DO、pH、污泥沉降比SV30逐级定位病根。 |
| [`dayan-epc-boq-unbalanced-bid`](../skills/dayan-epc-boq-unbalanced-bid/SKILL.md) | 在工程投标锁价或甲方清标阶段，测算早收款项与预计调增子目的单价浮动安全区间，防范废标与低价亏本项。 |
| [`dayan-epc-fire-code-audit`](../skills/dayan-epc-fire-code-audit/SKILL.md) | 严格依据GB55037建筑防火通用规范全文强条，在装饰改造与机电安装报验前逐项排查疏散、封堵、防排烟硬伤。 |
| [`dayan-epc-material-price-diff`](../skills/dayan-epc-material-price-diff/SKILL.md) | 针对铜缆、钢材、商砼等大宗主材波动，按施工期造价信息价与±5%风险幅度公式精确计算竣工结算可补差额。 |
| [`dayan-epc-safety-hazard-log`](../skills/dayan-epc-safety-hazard-log/SKILL.md) | 对照住建部37号令危大工程目录，排查深基坑、高支模、起重吊装专项方案专家论证红线与劳务班组早班交底闭环。 |
| [`dayan-epc-subcontract-back2back`](../skills/dayan-epc-subcontract-back2back/SKILL.md) | 依据最高院背靠背条款批复精神，排查建设工程与机电分包合同中的收到总包款再付陷阱，给出结算兜底替换条款。 |
| [`dayan-epc-visa-expire-radar`](../skills/dayan-epc-visa-expire-radar/SKILL.md) | 排查装饰机电市政项目中的口头变更、超28天逾期失权签证项，生成带影像部位与造价测算的规范联系单闭环。 |
| [`dayan-erp-crm-agent-bridge`](../skills/dayan-erp-crm-agent-bridge/SKILL.md) | 针对企业自建扣子、Dify或本地知识库回答不准、难以衔接现有ERP/CRM的问题，输出源头治理与受控接入方案。 |
| [`dayan-ev-bess-peak-shaving`](../skills/dayan-ev-bess-peak-shaving/SKILL.md) | 戳破储能厂家“三年回本”PPT泡沫！扣除DOD放电深度、充放转换效率86%、电芯逐年衰减与消防运维，实测光储充真实IRR。 |
| [`dayan-ev-epc-hidden-cost`](../skills/dayan-ev-epc-hidden-cost/SKILL.md) | 报价单写320万，干到并网结账变480万！逐项清查10kV外线红线外顶管、重卡49吨重载混泥土地坪、消防雨棚与环评并网漏项。 |
| [`dayan-ev-fleet-offtake-audit`](../skills/dayan-ev-fleet-offtake-audit/SKILL.md) | 重卡站最怕建好后隔壁降价5分钱把车队全抢走！从保底度电刚性、油电联动调价、账期押金与违约赔偿四视角锁死大车队。 |
| [`dayan-ev-grid-demand-tariff`](../skills/dayan-ev-grid-demand-tariff/SKILL.md) | 专治重卡充电站投产首月被几万块基本电费打懵！精准计算容量计费与需量计费省钱切换点，拦截超核定需量105%双倍罚款刺客。 |
| [`dayan-ev-heavy-truck-tco`](../skills/dayan-ev-heavy-truck-tco/SKILL.md) | 拒绝卖车销售虚报续航！按重载爬坡真实电耗、电池衰减、冬季暖风折损与峰谷充电均价，算清电动重卡替换国六柴油车真实回本月数。 |
| [`dayan-ev-subsidy-acceptance`](../skills/dayan-ev-subsidy-acceptance/SKILL.md) | 别等建完才发现拿不到几十万建设运营补贴！提前核对备案主体、桩体CQC认证、省级监管平台直连上传率与竣工五方档案。 |
| [`dayan-exec-hiring-bs-detector`](../skills/dayan-exec-hiring-bs-detector/SKILL.md) | 专防花大价钱招来PPT大厂混子！把候选人简历里的『主导千万级增长/搭建体系』拆成颗粒度追问链与实战小考题，当场验出真本事。 |
| [`dayan-exec-stress-test`](../skills/dayan-exec-stress-test/SKILL.md) | 一键路由CFO财务、CMO市场、CCO留存、CDO数据、CISO安全与CAIO人工智能六大高管质疑官视角，对新预算、新产品或转型方案做残酷压测。 |
| [`dayan-export-spec-sync`](../skills/dayan-export-spec-sync/SKILL.md) | 比对跨境商品页、英文产品画册与报价单中的尺寸、重量、装箱数量、材质表述与贸易条款，提前发现跨表差异。 |
| [`dayan-factory-8d-quality`](../skills/dayan-factory-8d-quality/SKILL.md) | 大客户退货索赔火烧眉毛！严禁拿『员工粗心加强培训』糊弄审核员，用5Why双路径（发生因+流出因）生成专业8D质量改善报告。 |
| [`dayan-factory-bom-shortage`](../skills/dayan-factory-bom-shortage/SKILL.md) | 专治销售拍胸脯接急单、车间干到一半发现缺一颗螺丝停线！快速核算BOM物料齐套缺口、产线换模损耗与被挤占老订单延期代价。 |
| [`dayan-fde-pilot-prd-writer`](../skills/dayan-fde-pilot-prd-writer/SKILL.md) | 将业务部门的提效设想转化为业务人员与开发工程师都能清晰对齐的单流程试点方案、字段契约与验收清单。 |
| [`dayan-feishu-bitable-architect`](../skills/dayan-feishu-bitable-architect/SKILL.md) | 传统软件几十万太笨重、普通Excel多人改就乱套！帮20-200人团队设计表结构关联、行列权限隔离、AI字段自动提取与飞书群催办流。 |
| [`dayan-food-batch-recall-trace`](../skills/dayan-food-batch-recall-trace/SKILL.md) | 飞行检查组现场抽一袋成品让你2小时内调出辣椒花椒农残快检单、投料记录与流向经销商名单，翻箱倒柜找不齐直接停产整顿！ |
| [`dayan-food-dealer-rebate-recon`](../skills/dayan-food-dealer-rebate-recon/SKILL.md) | 每到季末财务和大区经理吵翻天：满十赠一、陈列堆头费、临期退换补贴、窜货罚款全记在微信聊天里算成糊涂账！一键拉平返利兑付。 |
| [`dayan-food-gb7718-antitroll`](../skills/dayan-food-gb7718-antitroll/SKILL.md) | 十万张包装袋印出来才发现漏标致敏原、写了“零添加”或净含量字高差1毫米，被职业打假人买空十倍索赔！印前逐项清零标签死角。 |
| [`dayan-food-oem-recipe-quoter`](../skills/dayan-food-oem-recipe-quoter/SKILL.md) | 按生料成本加20%给连锁餐饮报价，炒出来才发现水分挥发收率只有82%、挂锅死耗25公斤，干一单亏一单！精准算出500kg/2T/10T保本含税价。 |
| [`dayan-food-private-label-contract`](../skills/dayan-food-private-label-contract/SKILL.md) | 主播喊着能卖十万单让你备齐50万个专版彩袋，结果播一场凉了拍屁股走人，几十万印死他LOGO的包材全烂在你仓库！ |
| [`dayan-freight-customs-checker`](../skills/dayan-freight-customs-checker/SKILL.md) | 错一个HS编码或箱单毛重不一致就要改单罚钱耽误船期！交叉核对商业发票、装箱单、提单草件与信用证条款，生成客户异常沟通中英文函。 |
| [`dayan-geo-ai-seo`](../skills/dayan-geo-ai-seo/SKILL.md) | 针对豆包、DeepSeek、元宝、Kimi、ChatGPT与Perplexity的采购提问链路，诊断品牌为何不被推荐，设计站内结构化事实与第三方信源矩阵。 |
| [`dayan-geo-visibility-check`](../skills/dayan-geo-visibility-check/SKILL.md) | 围绕真实买方选型提问，协助梳理企业在主流搜索与AI问答中的信息缺口、同名混淆情况与内容优化次序。 |
| [`dayan-grid-copper-price-escalator`](../skills/dayan-grid-copper-price-escalator/SKILL.md) | 针对交期6-18个月的出海变压器与开关柜订单，设计挂钩LME铜价、取向硅钢指数与美元汇率的合同价格联动条款。 |
| [`dayan-grid-heavy-lift-lc-guard`](../skills/dayan-grid-heavy-lift-lc-guard/SKILL.md) | 管控大型主变充氮运输三维冲击记录仪免责边界、特种框架箱绑扎及远期信用证“目的港业主签字才议付”软条款。 |
| [`dayan-grid-loss-penalty-toc`](../skills/dayan-grid-loss-penalty-toc/SKILL.md) | 核算国际电网招标中的空载损耗A因子与负载损耗B因子总拥有成本TOC，严防超保证损耗触发天价美元罚金或退货。 |
| [`dayan-grid-switchgear-bom-guard`](../skills/dayan-grid-switchgear-bom-guard/SKILL.md) | 在成套电气盘厂快速报价阶段，交叉核对一次主接线图、断路器分断能力、铜排规格、微机综保与弧光保护漏项。 |
| [`dayan-grid-ul-kema-cert-check`](../skills/dayan-grid-ul-kema-cert-check/SKILL.md) | 在接海外电网与工业大项目前，快速核清北美UL/cUL、欧洲KEMA突发短路型式试验及沙特SEC/阿联酋DEWA短名单门槛。 |
| [`dayan-grid-xfmr-spec-deviation`](../skills/dayan-grid-xfmr-spec-deviation/SKILL.md) | 针对欧美中东百页英文变压器标书，逐项比对IEC60076与IEEE-C57温升、阻抗公差、绝缘水平与油漆防腐偏离。 |
| [`dayan-hotel-homestay-revpar`](../skills/dayan-hotel-homestay-revpar/SKILL.md) | 携程美团评分掉0.1分流量掉三成！诊断入住率OCC与平均房价ADR平衡点、差评高情商公开回复模板，并补齐AI旅行规划推荐词条。 |
| [`dayan-humanize-pro`](../skills/dayan-humanize-pro/SKILL.md) | 系统清洗中文文稿里的赋能、抓手、闭环、排比三连、万能过渡与空洞结尾等AI腔，按老板汇报、客户提案、公众号等场景校准真人语感。 |
| [`dayan-it-acceptance-signoff-pack`](../skills/dayan-it-acceptance-signoff-pack/SKILL.md) | 倒推财政与国企信息化项目审计审计数十项严苛要求，提前备齐需求跟踪矩阵、第三方测评、试运行日志与培训签到闭环。 |
| [`dayan-it-channel-integrator-split`](../skills/dayan-it-channel-integrator-split/SKILL.md) | 理清原厂ISV、本地总集成商与居间引荐伙伴的客户报备保护期、撞单裁决、定制二开成本扣除与回款分润结算规则。 |
| [`dayan-it-presales-poc-script`](../skills/dayan-it-presales-poc-script/SKILL.md) | 在答应大客户免费POC概念验证前，锁定3项可量化成功标准、脱敏样本范围与测试后转商签时间表，拒绝无底洞定制陪跑。 |
| [`dayan-it-scope-creep-firewall`](../skills/dayan-it-scope-creep-firewall/SKILL.md) | 帮软件外包、政企信息化与AI定制团队把甲方“顺手改一下”的口头加活，体面转化为带工时报价的书面变更单（CR）。 |
| [`dayan-it-sla-incident-postmortem`](../skills/dayan-it-sla-incident-postmortem/SKILL.md) | 当SaaS或客户生产系统发生故障恢复后，用5-Why挖出架构真根因并同步生成不推诿、稳信任的对客正式说明函。 |
| [`dayan-it-xinchuang-compat-matrix`](../skills/dayan-it-xinchuang-compat-matrix/SKILL.md) | 梳理政企信创项目中的鲲鹏海光飞腾CPU、麒麟统信OS、达梦人大金仓数据库及中间件交叉互认证矩阵与迁移工时。 |
| [`dayan-kb-clean-data-governor`](../skills/dayan-kb-clean-data-governor/SKILL.md) | 在将企业制度、产品资料与常见问答导入知识库前，协助排查前后口径差异、补齐生效范围并优化段落结构。 |
| [`dayan-lab-reagent-std-expiry`](../skills/dayan-lab-reagent-std-expiry/SKILL.md) | 统筹管理实验室有证标准物质（CRM）开封效期、天平色谱强检周期及易制毒易制爆试剂双人双锁领用台账。 |
| [`dayan-law-cpa-intake-triage`](../skills/dayan-law-cpa-intake-triage/SKILL.md) | 解放合伙人每天免费陪聊两小时白嫖咨询！快速梳理当事人/企业主案情时间线、核心诉求证据缺口，设计付费首诊与阶梯代理服务包。 |
| [`dayan-lc-cdu-thermal-sizing`](../skills/dayan-lc-cdu-thermal-sizing/SKILL.md) | 梅雨季机房湿度一升，CDU供液温度设低2度就在分水器和冷板上挂满冷凝水珠！精准校核板换换热裕度、N+1循环泵切换与露点安全垫。 |
| [`dayan-lc-datacenter-pue-roi`](../skills/dayan-lc-datacenter-pue-roi/SKILL.md) | 老机房单柜只能跑8kW风冷且PUE高达1.58面临阶梯加价电费处罚！算清行级背板/冷板液冷改造CapEx、腾退空间增插GPU收益与电费回本期。 |
| [`dayan-lc-leak-liability-contract`](../skills/dayan-lc-leak-liability-contract/SKILL.md) | 卖一套3万元的Manifold快接头，甲方合同里写“若发生渗漏赔偿机柜内全部H200/GB200服务器及算力停机损失”：漏一次3000万直接让工厂破产！ |
| [`dayan-lc-oem-qualification-pack`](../skills/dayan-lc-oem-qualification-pack/SKILL.md) | 国产液冷件精度完全不输欧美大牌，却因为拿不出标准RFI英文可靠性证据包、FMEA与洁净度颗粒报告，在台系和北美服务器厂初审就被刷掉！ |
| [`dayan-lc-uqd-cv-leakcheck`](../skills/dayan-lc-uqd-cv-leakcheck/SKILL.md) | 120kW高密AI机柜选小了UQD通径直接把二次侧泵扬程憋死，插拔滴出一滴冷却液就烧穿百万级GPU刀片！精准校核Cv压降与溢液红线。 |
| [`dayan-lc-wet-material-compat`](../skills/dayan-lc-wet-material-compat/SKILL.md) | 同一条二次侧回路里混装了紫铜冷板和铝制集分水器，半年后原电池电偶腐蚀穿孔漏液、绿藻菌泥把流道全糊死！严把湿材料兼容白名单。 |
| [`dayan-legacy-excel-cleaner`](../skills/dayan-legacy-excel-cleaner/SKILL.md) | 专治十年老厂一物五名、合并单元格满天飞、日期金额格式全乱的历史脏表格！设计标准化主数据编码规则与零误删Python/公式清洗脚本。 |
| [`dayan-liquor-box-diecut-cost`](../skills/dayan-liquor-box-diecut-cost/SKILL.md) | 礼盒厂最惨就是算对纸价却漏算大面积电化铝烫金废品率、异形刀版模切慢工与手工糊盒胶水，十万套交完一分没赚！ |
| [`dayan-local-llm-hardware-sizer`](../skills/dayan-local-llm-hardware-sizer/SKILL.md) | 别听卖服务器厂商忽悠先砸五十万买显卡吃灰！按并发人数、上下文长度与量化精度精算DeepSeek/Qwen私有部署显存需求及云API三年总账对比。 |
| [`dayan-loss-line-stop-bleed`](../skills/dayan-loss-line-stop-bleed/SKILL.md) | 剔除沉没成本执念！算清继续硬撑3个月的失血账与立即关停/转租/缩编的一次性遣散止损账，帮老板果断砍掉失血包袱。 |
| [`dayan-med-ad-law-redline`](../skills/dayan-med-ad-law-redline/SKILL.md) | 依据医疗广告管理办法与平台审核尺度，秒查小红书、抖音、美团团购文案里的功效断言、前后对比与绝对化违禁词。 |
| [`dayan-med-informed-consent-guard`](../skills/dayan-med-informed-consent-guard/SKILL.md) | 排查消费医疗门诊术前告知书模板漏项、预期效果过度承诺与病历书写时间逻辑硬伤，筑牢医疗纠纷举证证据链。 |
| [`dayan-meeting-to-accountability`](../skills/dayan-meeting-to-accountability/SKILL.md) | 治好『会上激动、会后不动』！从杂乱口语会议转写稿里精准剥离拍板决议、唯一责任人、交付物标准、截止日期与未决争议。 |
| [`dayan-mg-crush-inrush-sizing`](../skills/dayan-mg-crush-inrush-sizing/SKILL.md) | 针对非洲东南亚矿山球磨机、破碎机、渣浆泵5-7倍启动冲击电流，校核离网构网型PCS短时过载倍数与变压器阻抗。 |
| [`dayan-mg-diesel-pv-ems-fuel`](../skills/dayan-mg-diesel-pv-ems-fuel/SKILL.md) | 测算海外高价柴油（$1.2-$1.8/L）矿区工厂加装光伏储能后的真实节油率，同时锁死柴发30%最低负载率防积碳报废。 |
| [`dayan-mg-fob-fullpay-release`](../skills/dayan-mg-fob-fullpay-release/SKILL.md) | 针对尼日利亚、南非、巴基斯坦、拉美等高外汇管制市场，设计发货前付清全款或保兑信用证、防目的港弃货压价铁律。 |
| [`dayan-mg-harsh-heat-derating`](../skills/dayan-mg-harsh-heat-derating/SKILL.md) | 针对中东沙漠50-55℃极热、海岛高盐雾与矿山高粉尘工况，校核PCS超过45℃功率线性降额、液冷自耗电与C5防腐。 |
| [`dayan-mg-multilang-field-triage`](../skills/dayan-mg-multilang-field-triage/SKILL.md) | 把微电网现场最常见的绝缘阻抗低、BMS通讯断、柴发同期失败与黑启动步骤，编译成英法西俄傻瓜图文排错卡。 |
| [`dayan-mg-un3536-dg-shipping`](../skills/dayan-mg-un3536-dg-shipping/SKILL.md) | 逐项核对出口锂电储能柜UN38.3、UN3536危包证/船级社柜证、SOC≤30%荷电状态及目的港危险品堆场免堆期。 |
| [`dayan-multi-agent-arch`](../skills/dayan-multi-agent-arch/SKILL.md) | 先按『规则>Pipeline>单Agent>总控专家>并发审查』五级阶梯砍掉伪多智能体复杂度，再输出任务、角色、状态与熔断四件套。 |
| [`dayan-oa-doc-cross-checker`](../skills/dayan-oa-doc-cross-checker/SKILL.md) | 面向多页方案、采购协议、验收材料与预算表格，逐项核对主体全称、金额合计、时间节点与附件编号一致性。 |
| [`dayan-okr-kpi-decomposer`](../skills/dayan-okr-kpi-decomposer/SKILL.md) | 拒绝年底拍脑袋喊『明年翻倍』、开年各部门各干各的！按老客留存、客单升维与新客漏斗把年度营收倒推成市场、销售、交付每月的领先指标。 |
| [`dayan-order-change-erp-guard`](../skills/dayan-order-change-erp-guard/SKILL.md) | 当客户提出规格、交期、数量或包装变更时，自动梳理销售、工程、采购、生产与财务的协同确认清单。 |
| [`dayan-org-ai-ct`](../skills/dayan-org-ai-ct/SKILL.md) | 从老板救火地图、跨部门信息断点与老师傅隐性经验三个切口给企业做AI就绪度CT体检，精准筛出3条30天见效的MVP落地流程。 |
| [`dayan-partner-equity-guard`](../skills/dayan-partner-equity-guard/SKILL.md) | 专治五五平分僵局、兼职股东白拿干股与合伙人中途散伙带走股份！输出控制权结构、四年成熟期动态兑现与回购计价核心条款要点。 |
| [`dayan-pet-clinic-geo-check`](../skills/dayan-pet-clinic-geo-check/SKILL.md) | 半夜两点猫咪尿闭，宠主问豆包和美团“附近靠谱24小时宠物急诊”，推荐名单里根本没你家！排查同城AI找院断点并补齐信源。 |
| [`dayan-pet-dental-imaging-sop`](../skills/dayan-pet-dental-imaging-sop/SKILL.md) | 同样看耳朵发炎，销冠医生顺手转化1800元全口牙片洁治，新手医生只开60元耳药！把名医五步视诊话术编译成全院可复制SOP。 |
| [`dayan-pet-drug-compliance`](../skills/dayan-pet-drug-compliance/SKILL.md) | 专治宠物医院药房被职业举报“假兽药/违规用人药”重罚！核验兽药字批文、拦截猫用对乙酰氨基酚等致死禁忌、锁死急需人用药双签。 |
| [`dayan-pet-postop-retention`](../skills/dayan-pet-postop-retention/SKILL.md) | 绝育洗牙做完就躺尸企微好友列表，驱虫药全跑去网店买！用3-7-21天专业康复节点随访赢取信任，自然锁死年度体检驱虫卡。 |
| [`dayan-pet-triage-consent`](../skills/dayan-pet-triage-consent/SKILL.md) | 手术很成功，但术后突发隐匿性肥厚型心肌病肺水肿引发天价医闹！按ASA麻醉分级定制个性化术前告知与放弃检查签字完整核销。 |
| [`dayan-pet-vaccine-coldchain`](../skills/dayan-pet-vaccine-coldchain/SKILL.md) | 一冰箱进口猫三联和单抗因周末跳闸报废亏掉几万，临期试纸放到过期没人管！建立2–8℃双路冷链台账与90/60/30天临期清仓机制。 |
| [`dayan-pmr-blackmass-nicoli-coef`](../skills/dayan-pmr-blackmass-nicoli-coef/SKILL.md) | 核算三元与磷酸铁锂电池黑粉回收中的镍钴锂金属折算系数、碳酸锂联动价及氟磷铜铝铁水分超标阶梯扣款。 |
| [`dayan-pmr-blind-sampling-moisture`](../skills/dayan-pmr-blind-sampling-moisture/SKILL.md) | 制定废催化剂、电路板泥与黑粉买卖双方现场混匀、圆锥四分法缩分、三份铅封留样及超差第三方CMA仲裁标准。 |
| [`dayan-pmr-cash-escrow-antifraud`](../skills/dayan-pmr-cash-escrow-antifraud/SKILL.md) | 针对单车数百万现款交割的废催化剂、银浆与铜镍废料收购，建立防夹层灌铅水、防过磅遥控器与铅封押运十步铁律。 |
| [`dayan-pmr-futures-hedge-guard`](../skills/dayan-pmr-futures-hedge-guard/SKILL.md) | 算清收料点价到成品金属出库15-30天加工周期内的净库存敞口，匹配广期所碳酸锂与上期所金银铂钯空头套保手数。 |
| [`dayan-pmr-hw50-manifest-compliance`](../skills/dayan-pmr-hw50-manifest-compliance/SKILL.md) | 严格核查危险废物经营许可证核准八位代码（如HW50/HW49）、跨省转移商请批复、危货运输资质与全国固废网联单。 |
| [`dayan-pmr-pgm-assay-settlement`](../skills/dayan-pmr-pgm-assay-settlement/SKILL.md) | 针对石化医药精细化工废贵金属催化剂回收，精确计算干基扣水重、火法/湿法精炼计价系数、加工费与点价结算额。 |
| [`dayan-pool-dealer-channel-matcher`](../skills/dayan-pool-dealer-channel-matcher/SKILL.md) | 变频泳池泵在亚马逊卷低价只能赚辛苦钱，真正70%毛利全在欧美线下Pool-Builder安装商和区域泳池批发商手里！教你用渠道厚利切开封闭圈子。 |
| [`dayan-pool-inverter-doe-roi`](../skills/dayan-pool-inverter-doe-roi/SKILL.md) | 美国DOE法规早已禁售绝大多数大马力高耗能单速过滤泵！算准WEF加权能源因子合规底线，并生成让欧美房主12个月省回泵钱的可视化电费单。 |
| [`dayan-pool-territory-exclusivity`](../skills/dayan-pool-territory-exclusivity/SKILL.md) | 老外一上来就画大饼要签全美或全德5年独家总代，结果一年只提半个小柜把你的整个国家市场活活锁死！用阶梯提货脱钩条款守住主动权。 |
| [`dayan-pool-wras-nsf50-cert`](../skills/dayan-pool-wras-nsf50-cert/SKILL.md) | 接了欧洲商超和北美大渠道的泳池泵与滤芯整柜大单，审厂时拿不出NSF/ANSI 50浸出毒理报告或Wi-Fi模块缺CE-RED网络安全认证卡死交期！ |
| [`dayan-private-board`](../skills/dayan-private-board/SKILL.md) | 由AI私董官控场、多位经历迥异的实战派幕僚轮番开放式发问，严禁好为人师给鸡汤建议，陪创始人一层层照见关键经营决策背后的真盲区。 |
| [`dayan-private-domain-wecom-sop`](../skills/dayan-private-domain-wecom-sop/SKILL.md) | 加了五千个客户微信却不敢发声、一发硬广就被删！为高客单B2B与高净值消费品设计黄金首周破冰、朋友圈人设日历与沉默老客激活剧本。 |
| [`dayan-prompt-contract`](../skills/dayan-prompt-contract/SKILL.md) | 拒绝堆砌玄学咒语！通过7格欠参诊断把模糊需求锻造成包含角色边界、工作流、质量验收线、注入防御与红线的生产级Prompt合约。 |
| [`dayan-rag-guardrail-kb`](../skills/dayan-rag-guardrail-kb/SKILL.md) | 拒绝胡编乱造的全知问答框！按安全预过滤、权威版签字、过期熔断、原文接地四态兜错与老板缺口看板五道关卡设计企业知识库。 |
| [`dayan-rank-reducer`](../skills/dayan-rank-reducer/SKILL.md) | 输入一个行业、竞品、复杂产品需求或棘手经营困局，用七步递归下沉与难以变更测试砍掉十几个表象，挖出真正支撑全局的最小独立力（秩）。 |
| [`dayan-restaurant-chain-audit`](../skills/dayan-restaurant-chain-audit/SKILL.md) | 专治餐饮老板看堂食外卖挺热闹、月底一算账全给平台和房东打工！精算食材损耗、人工人效、美团抖音扣点补贴后的真实单店净现金流。 |
| [`dayan-role-training-architect`](../skills/dayan-role-training-architect/SKILL.md) | 围绕企业真实岗位工作，按经营决策层、销售运营行政业务岗或客户主题沙龙，定制带实操练习与核对方法的培训方案。 |
| [`dayan-sales-commission-design`](../skills/dayan-sales-commission-design/SKILL.md) | 防止销售为拿提成乱打折亏毛利、签完单不管回款！按实收回款与真实毛利双挂钩测算底薪提成阶梯，跑完极端算账模拟再发制度。 |
| [`dayan-sales-visit-to-crm`](../skills/dayan-sales-visit-to-crm/SKILL.md) | 将零散的客户拜访笔记、电话沟通要点整理为结构化CRM字段、需求成熟度梳理与下一步跟进待办。 |
| [`dayan-semi-cleanroom-pack-sop`](../skills/dayan-semi-cleanroom-pack-sop/SKILL.md) | 零件尺寸公差全合格，只因超净间内袋封口前多沾了3颗0.3微米尘粒或水痕，到晶圆厂拆包上机直接切分维度爆表整批退货！ |
| [`dayan-semi-coa-trace-impurity`](../skills/dayan-semi-coa-trace-impurity/SKILL.md) | 铁钠钾铜镍痕量金属只要有一项超标几个ppb，进12寸晶圆扩散炉就能污染整批百万美金Wafer！逐项核对ICP-MS实测值与炉批号溯源链。 |
| [`dayan-semi-cylinder-consign-recon`](../skills/dayan-semi-cylinder-consign-recon/SKILL.md) | 一只内壁电抛光316L电子特气Y瓶造价几万元，发去客户厂区半年不退瓶，周转率掉一半直接把利润全压死在钢瓶和寄售备件里！ |
| [`dayan-semi-qual-wafer-liability`](../skills/dayan-semi-qual-wafer-liability/SKILL.md) | 一只要价8000元的国产石英环送进Fab厂做Qual验证，要是没锁死免责上限，一旦腔体异常刮花25片12寸晶圆，客户反手索赔两百万！ |
| [`dayan-semi-quartz-sic-yield-quoter`](../skills/dayan-semi-quartz-sic-yield-quoter/SKILL.md) | 石英舟、喷淋头微孔或碳化硅聚焦环在超声精雕最后一道崩一道0.2mm暗裂，整块上万元进口锭料全废！按复合直通率倒推真保本价。 |
| [`dayan-semi-s2-f47-compliance`](../skills/dayan-semi-s2-f47-compliance/SKILL.md) | 真空阀门模组、尾气Scrubber或温控Chiller卖进晶圆厂，EHS安全官一审SEMI S2互锁和F47抗晃电不过关直接卡死验收尾款！ |
| [`dayan-ship-class-cert-matcher`](../skills/dayan-ship-class-cert-matcher/SKILL.md) | 海工平台和远洋船换一块高强钢板或主机曲轴连杆，供应商只给了一张工厂自检3.1证书没办船级社验船师现场见证的3.2船检证，焊上去被验船师勒令全部割掉重做！ |
| [`dayan-ship-demurrage-force-majeure`](../skills/dayan-ship-demurrage-force-majeure/SKILL.md) | 接一单60万美元的坞修改装，老外合同写延误一天罚2.5万美元无上限且放弃留置船只权利：赶上台风停航5天加船东赖尾款，船厂直接车船两空！ |
| [`dayan-ship-drydock-spec-auditor`](../skills/dayan-ship-drydock-spec-auditor/SKILL.md) | 希腊和挪威船东发来200页英文Docking Spec，隐藏着“Including all necessary staging, cleaning and testing”全包坑，进坞开舱后追加工程VO漏签单直接白干几百万！ |
| [`dayan-ship-imo-cii-scrubber-roi`](../skills/dayan-ship-imo-cii-scrubber-roi/SKILL.md) | 老船CII连拿D级或跌入E级面临欧洲大租家退租与EU ETS巨额碳配额账单！算清加装脱硫塔烧高低硫油差价、风力助推转子与有机硅防污漆真实回本月数。 |
| [`dayan-ship-offshore-ndt-weld-log`](../skills/dayan-ship-offshore-ndt-weld-log/SKILL.md) | 海工导管架和LNG低温双壁管都焊完了，业主QA一查发现焊工资格证缺6G全位置覆盖、或者特种合金焊缝漏做100%射线+相控阵超声探伤，整段管系推倒重来！ |
| [`dayan-ship-spares-impa-quoter`](../skills/dayan-ship-spares-impa-quoter/SKILL.md) | 外轮在新加坡或舟山锚地只停靠14小时，机务发来500行乱七八糟英文缩写和IMPA六位码询价单，人工翻大字典报价慢半拍订单直接被对手抢走，报错防爆等级还上不了船！ |
| [`dayan-sichuan-token-voucher-roi`](../skills/dayan-sichuan-token-voucher-roi/SKILL.md) | 结合企业实际单据量与岗位工时，算清模型调用与工程实施成本结构，评估优先推进场景的预期经营回报。 |
| [`dayan-slide-deck`](../skills/dayan-slide-deck/SKILL.md) | 先立视觉方向与每页唯一结论契约，再生成16:9高管级HTML演示文稿与可编辑PPTX逐页结构，彻底告别廉价套模板感。 |
| [`dayan-sop-extractor-master`](../skills/dayan-sop-extractor-master/SKILL.md) | 不怕销冠跳槽、老师傅退休断代！通过情景追问与成败对比访谈，把老手脑子里说不清的『凭手感经验』翻成新人照着就能干的SOP与AI提示词。 |
| [`dayan-spa-consumable-replenish`](../skills/dayan-spa-consumable-replenish/SKILL.md) | 每年4月北美开池季一到爆单断货看着对手数钱，9月入秋晚到一柜货又在海外仓交一整年高额仓储费！掐准季节指数算死翻单起运日。 |
| [`dayan-spa-filter-crossref-guard`](../skills/dayan-spa-filter-crossref-guard/SKILL.md) | SPA滤芯毛利超55%且每3个月必换，但全美几百种浴缸型号只要总长差4毫米、SAE粗牙和MPT细牙搞混，一整柜货在亚马逊退货率飙上25%直接封链接！ |
| [`dayan-supplier-price-slasher`](../skills/dayan-supplier-price-slasher/SKILL.md) | 防止采购吃暗亏或只看总价被配件辅料宰一刀！按BOM成本结构反推供应商真实毛利空间，生成三家同口径比价矩阵与阳光降本谈判剧本。 |
| [`dayan-svg-diagram`](../skills/dayan-svg-diagram/SKILL.md) | 先判该不该画图，再用深蓝印刷感色板与精确手算坐标生成零重叠、一图一结论的单文件SVG系统架构图、流程图、时序图与决策树。 |
| [`dayan-tender-redline-audit`](../skills/dayan-tender-redline-audit/SKILL.md) | 协助商务与售前团队梳理招标公告与采购文件，提取准入资格条件、实质性响应条款、评分结构与封标前检查项。 |
| [`dayan-weekly-report-truth`](../skills/dayan-weekly-report-truth/SKILL.md) | 把满篇『持续推进、积极协调、赋能协同』的糊弄式周报一键榨干水分，揪出逾期未闭环事项、跨部门扯皮点与需要老板拍板的真雷区。 |
| [`dayan-zhuanjingtexin-grant`](../skills/dayan-zhuanjingtexin-grant/SKILL.md) | 别花几万找黑中介套烂模板被刷下！对照高新技术企业与专精特新硬指标自检知识产权、研发费占比与细分市场补短板证明逻辑。 |
