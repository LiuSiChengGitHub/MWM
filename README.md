# 医疗世界模型（MWM）数据处理启动仓库

这个仓库面向“医疗世界模型 / 围术期世界模型”课题的数据处理起步阶段，当前重点是熟悉 `MIMIC-IV`、建立数据理解框架、整理后续可执行任务，并把项目说明沉淀下来，方便你后面边做边查。

## 1. 你现在在做什么

根据老师启动会说明，这个课题的目标不是只做一个分类器，而是想做一个**医疗世界模型**：

- 把患者状态看成会随时间变化的“系统状态”
- 把临床干预看成“动作 / 控制变量”
- 让模型能够预测未来状态轨迹，而不只是输出一个标签
- 支持风险预测、反事实推理、治疗规划、决策辅助

老师目前给出的围术期方向重点是：

- 利用术前基础特征
- 结合术中波形和其他术中数据
- 预测术中大出血、术中低血压、术后并发症等结局

你被分在**数据处理组**，所以你近期最核心的工作不是“发明模型”，而是：

- 弄清楚数据里有什么
- 找到能用的表和字段
- 定义 cohort（研究人群）
- 定义 label（预测目标）
- 把原始数据变成可训练的数据集

这对零基础同学完全正常，而且这往往就是项目能不能推进的关键环节。

## 2. 这个课题大概在干什么

一句话版：

**从多模态临床时间序列里学习“患者状态如何在干预下演化”，并进一步做预测、模拟和决策支持。**

更接地气一点，可以把它分成三层理解：

1. `普通预测任务`
   例如预测某个病人会不会低血压、会不会出血、会不会出现术后并发症。
2. `时间序列建模`
   不只看单个时间点，而是看患者状态随时间如何变化。
3. `世界模型`
   不只预测“会不会发生”，而是试图回答：
   - 现在患者处于什么隐藏状态？
   - 如果采取不同干预，未来轨迹会怎么变？
   - 哪种方案风险更低、结局更好？

你现在不用一开始就把这些都学透。现阶段只需要先接受一个框架：

**世界模型 = 比普通监督学习更强调“状态、动作、时间、未来轨迹”的模型。**

## 3. 为什么先用 MIMIC-IV

`MIMIC-IV` 是 MIT/PhysioNet 发布的去标识化临床数据库，包含医院、ICU、急诊等多来源电子病历数据，适合做：

- 临床时间序列建模
- 风险预测
- 患者轨迹建模
- 多表关联和数据工程
- 医疗大模型/世界模型的预训练或原型验证

它的优点是：

- 公开、经典、社区资料多
- 表结构清晰，适合练数据处理
- 有住院、ICU、急诊等多层级数据
- 有诊断、检验、生命体征、用药、转科、操作、部分文本

但要注意一个非常重要的现实问题：

**MIMIC-IV 本身并不是一个标准的“围术期高频手术室数据集”。**

基于你当前下载的版本和官方模块说明，可以合理推断：

- 它非常适合做住院/ICU/急诊患者状态建模
- 也适合训练多表清洗、对齐、标签构造流程
- 但它不直接等价于“术中高频波形 + 麻醉全过程”数据

所以你后续很可能会遇到两种情况：

- 用 `MIMIC-IV` 先做数据管线和原型任务
- 后面再接入更贴近围术期的数据源

这点你要尽早心里有数，不然容易把“围术期世界模型”和“MIMIC-IV 原始内容”混为一谈。

## 4. 你本地已经有哪些数据

当前数据放在仓库外的 `../datasets_MWM/`。

已确认存在：

- `mimic-iv-3.1.zip`
- `mimic-iv-ed-2.2.zip`
- `mimic-iv-3.1/mimic-iv-3.1/hosp/*.csv.gz`
- `mimic-iv-3.1/mimic-iv-3.1/icu/*.csv.gz`
- `mimic-iv-ed-2.2/mimic-iv-ed-2.2/ed/*.csv.gz`
- `mimic-iv-note_2.2/mimic-iv-note-deidentified-free-text-clinical-notes-2.2.zip`

注意：

- `note` 部分目前还是 zip，尚未解压
- 原始数据不建议放进 Git 仓库

## 5. MIMIC-IV 怎么理解

先记住 5 个关键 ID：

- `subject_id`：患者级 ID
- `hadm_id`：一次住院级 ID
- `stay_id`：一次 ICU stay 或 ED stay 的 ID
- `itemid`：监测项 / 化验项字典 ID
- `icd_code`：诊断或操作编码

最常见的关系是：

- `patients` 通过 `subject_id` 连到患者
- `admissions` 通过 `hadm_id` 连到一次住院
- `icustays` 通过 `stay_id` 连到一次 ICU 住留
- `labevents`、`chartevents` 这类事件表承载时间序列数据

### 5.1 你这批数据包含哪些模块

#### `hosp`

偏住院 / 全院级结构化数据。

你最可能先接触这些表：

- `patients`
  - 表头：`subject_id, gender, anchor_age, anchor_year, anchor_year_group, dod`
- `admissions`
  - 表头：`subject_id, hadm_id, admittime, dischtime, deathtime, admission_type, ...`
- `diagnoses_icd`
  - 表头：`subject_id, hadm_id, seq_num, icd_code, icd_version`
- `labevents`
  - 表头：`labevent_id, subject_id, hadm_id, specimen_id, itemid, ... charttime, value, valuenum, valueuom, ...`
- `procedures_icd`
- `prescriptions`
- `transfers`
- `services`

字典表：

- `d_labitems`
  - 用于解释 `labevents.itemid`
- `d_icd_diagnoses`
  - 用于解释 `diagnoses_icd.icd_code`
- `d_icd_procedures`

#### `icu`

偏 ICU 时序数据，是后续建模最有可能用到的部分。

重点表：

- `icustays`
  - 表头：`subject_id, hadm_id, stay_id, first_careunit, last_careunit, intime, outtime, los`
- `chartevents`
  - 表头：`subject_id, hadm_id, stay_id, caregiver_id, charttime, storetime, itemid, value, valuenum, valueuom, warning`
- `inputevents`
- `outputevents`
- `procedureevents`
- `datetimeevents`

字典表：

- `d_items`
  - 用于解释 `chartevents/inputevents/...` 中的 `itemid`

#### `ed`

偏急诊过程数据，可用于补前置就诊信息和入院前状态。

重点表：

- `edstays`
  - 表头：`subject_id, hadm_id, stay_id, intime, outtime, gender, race, arrival_transport, disposition`
- `triage`
  - 表头：`subject_id, stay_id, temperature, heartrate, resprate, o2sat, sbp, dbp, pain, acuity, chiefcomplaint`
- `vitalsign`
  - 表头：`subject_id, stay_id, charttime, temperature, heartrate, resprate, o2sat, sbp, dbp, rhythm, pain`
- `diagnosis`
- `medrecon`
- `pyxis`

#### `note`

你本地 zip 里至少包含：

- `radiology.csv.gz`
- `radiology_detail.csv.gz`
- `discharge.csv.gz`
- `discharge_detail.csv.gz`

这部分后面如果要做多模态或文本增强，才需要重点展开。

### 5.2 新手最容易踩的坑

- `stay_id` 不是全库通用主键
  - ICU 和 ED 都有 `stay_id`，但语义不同，不能想当然直接跨模块对齐。
- `chartevents` 非常大
  - 不要一上来整表读进内存。
- `itemid` 必须查字典表
  - 否则你根本不知道某个变量代表什么。
- 时间戳多而杂
  - 常见时间字段包括 `admittime`、`charttime`、`storetime`、`intime`、`outtime`。
- 缺失值和单位问题很常见
  - 同一变量要注意单位、异常值、记录频率。
- `anchor_age` 和 `anchor_year` 是去标识化后的字段
  - 做年龄/年份分析时要注意其含义，不要当真实自然年份直接解释。

## 6. 你之后大概率会被分配什么任务

按数据处理组常见节奏，你后面最可能遇到这些工作：

### 6.1 数据摸底

- 每张核心表有多少行、多少列
- 关键字段是否缺失
- 各张表如何关联
- 哪些表最适合当前任务

### 6.2 定义研究对象（cohort）

例如：

- 只看 ICU 患者
- 只看急诊后入院患者
- 只看有某类诊断、化验或生命体征记录的人

### 6.3 定义预测目标（label）

例如：

- 住院死亡
- ICU 死亡
- 24 小时内低血压
- 某并发症
- 某类操作或转归

### 6.4 特征构造

常见会做：

- 静态特征：年龄、性别、种族、既往诊断
- 时间序列特征：生命体征、化验、输入输出、用药
- 时间窗汇总：最近 6 小时 / 12 小时 / 24 小时的统计量
- 文本特征：出院小结、影像报告

### 6.5 数据对齐

把不同表的数据按时间对齐到同一时间轴，例如：

- 以 ICU 入科时间为 `t0`
- 取前 24 小时输入作为模型输入
- 取之后 6 小时或 24 小时事件作为 label

### 6.6 形成标准化训练集

最终你们组往往要交付：

- 可复现的 cohort 选择脚本
- 可复现的标签构造脚本
- 训练/验证/测试划分
- 数据字典
- 一个可以直接喂给模型的中间表或张量文件

## 7. 你现在最值得做的第一批工作

如果老师还没继续分任务，你可以先准备这些“不会白做”的基础工作：

1. 画出主键关系图
   - `patients -> admissions -> icustays / edstays -> events`
2. 统计关键表的规模
   - 行数、列数、主键覆盖率、时间范围
3. 做一个字段字典草稿
   - 先从 `patients / admissions / icustays / labevents / chartevents / triage / vitalsign` 开始
4. 想 2 到 3 个“可快速试跑”的原型任务
   - ICU 低血压预测
   - ICU 不良结局预测
   - 急诊到住院转归预测
5. 明确一个最小可行数据管线
   - 读数据
   - 过滤 cohort
   - 抽取时间窗
   - 生成标签
   - 导出训练集

## 8. 你如何利用 AI 帮你推进

你已经明确说了：**就业关联不强，希望 AI 多做代码，你只需要理解大框架。**

这个合作方式完全可以，而且很适合当前阶段。建议把 AI 用在这些地方：

### 8.1 让 AI 帮你做“脏活累活”

- 写数据读取脚本
- 写多表 join 脚本
- 写缺失值统计和 EDA 脚本
- 写 cohort 筛选脚本
- 写 label 构造脚本
- 写 README、实验记录、周报草稿

### 8.2 让 AI 帮你“翻译论文 / 任务”

你可以直接问：

- 这篇论文的数据流是什么？
- 这个 label 怎么从 MIMIC-IV 里实现？
- 这个表和那个表怎么 join？
- 这个 baseline 代码在做什么？

### 8.3 让 AI 帮你“拆任务”

最实用的问法不是“帮我做科研”，而是：

- 把这个任务拆成 5 个脚本
- 给我一个最小可跑版本
- 帮我先实现第一步并解释输入输出

### 8.4 你自己要保留判断权的地方

- cohort 定义是否符合老师目标
- label 是否有临床意义
- 时间窗是否合理
- 评价指标是否符合任务
- 数据泄漏是否被避免

也就是说：

**代码可以高度依赖 AI，但研究设定最好和老师/师兄师姐对齐。**

## 9. 现阶段你只需要掌握的大框架

不求深，只求够用的话，你记住下面这条链就够了：

`课题目标 -> 研究对象 -> 数据表 -> 主键关联 -> 时间对齐 -> 标签构造 -> 训练集生成 -> 模型训练`

你当前的位置就在：

`数据表 -> 主键关联 -> 时间对齐 -> 标签构造`

## 10. 后续建议的推进顺序

建议按这个顺序做，不容易乱：

1. 先认表，不急着建模
2. 先做小样本 EDA，不急着整库扫描
3. 先做一个能跑通的 prototype，不急着追求复杂 SOTA
4. 先把数据流程写稳定，再考虑世界模型结构

## 11. 官方资料与参考

- MIMIC-IV v3.1: <https://physionet.org/content/mimiciv/3.1/>
- MIMIC-IV-ED v2.2: <https://physionet.org/content/mimic-iv-ed/2.2/>
- MIMIC-IV 数据集论文（PubMed）: <https://pubmed.ncbi.nlm.nih.gov/36596836/>
- MIMIC-IV-ED 数据集论文（PubMed）: <https://pubmed.ncbi.nlm.nih.gov/39387475/>
- 老师提到的 Medical World Model 论文摘要页: <https://arxiv.org/abs/2506.02327>
- 老师文本中给出的项目页: <https://yijun-yang.github.io/MeWM/>

## 12. 这个仓库接下来适合放什么

后续建议把这个仓库用于放置：

- 数据处理脚本
- SQL / pandas 数据抽取逻辑
- EDA 笔记
- label 定义说明
- 实验配置
- 周报素材

而不要把下面这些直接提交到 Git：

- 原始 MIMIC 数据
- 大体积中间缓存
- 模型权重
- 临时导出结果

---

如果你愿意，下一步我可以继续直接帮你做下面这些具体工作中的任意一个：

- 生成一份 `MIMIC-IV` 主键关系图和表关系说明
- 写一个“读取并预览关键表”的脚本
- 给你搭一个最小的数据处理目录结构
- 先替你做第一个 EDA 脚本
