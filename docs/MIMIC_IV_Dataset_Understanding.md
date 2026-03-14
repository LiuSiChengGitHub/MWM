# MIMIC-IV 数据集理解说明

## 1. 当前数据集是否可读

当前本地数据集路径可以正常访问，以下两个路径都能读到同一份数据：

- `D:\Base\CodingSpace\datasets_MWM`
- `..\datasets_MWM`

我已经实际读取并验证了多张关键表，能够正常读取表头和样例行，包括：

- `hosp/patients.csv.gz`
- `hosp/admissions.csv.gz`
- `icu/icustays.csv.gz`
- `icu/chartevents.csv.gz`
- `ed/edstays.csv.gz`
- `ed/triage.csv.gz`
- `ed/vitalsign.csv.gz`

此外，我也确认 `note` 部分当前虽然还是 zip 包，但里面的文件列表可以正常读取。

## 2. 这个数据集本质上是什么

MIMIC-IV 不是一个单一任务的数据集，而是一个大型去标识化临床数据库。  
它更像一个“医院真实数据仓库”，里面保存了患者在住院、ICU、急诊等不同场景下留下的结构化记录，以及部分文本记录。

所以它不是那种“已经整理好、直接拿来训练”的现成样本表，而是：

- 多张表组成的数据系统
- 通过主键进行关联
- 带有大量时间信息
- 需要研究者自己定义研究对象、标签和特征

从研究角度看，它更像一个“数据底座”，而不是一个已经封装好的 benchmark 单任务文件。

## 3. 当前这份数据包含哪些模块

当前本地数据主要包含三部分：

- `mimic-iv-3.1`
- `mimic-iv-ed-2.2`
- `mimic-iv-note_2.2`

### 3.1 `hosp`

`hosp` 是住院级结构化数据，适合做住院层面的数据分析和标签构造。  
已经确认的关键表包括：

- `patients.csv.gz`
- `admissions.csv.gz`
- `diagnoses_icd.csv.gz`
- `labevents.csv.gz`
- `prescriptions.csv.gz`
- `procedures_icd.csv.gz`
- `transfers.csv.gz`

这些表主要对应：

- 患者基本信息
- 一次住院的信息
- 诊断编码
- 化验结果
- 用药记录
- 操作记录
- 转科过程

### 3.2 `icu`

`icu` 是 ICU 相关数据，也是时序信息最丰富的一部分。  
已经确认的关键表包括：

- `icustays.csv.gz`
- `chartevents.csv.gz`
- `inputevents.csv.gz`
- `outputevents.csv.gz`
- `procedureevents.csv.gz`
- `datetimeevents.csv.gz`

这些表主要记录：

- ICU stay 基本信息
- ICU 监护与生命体征
- 输入输出事件
- 过程性事件

这一模块非常适合后续做时间序列任务，也比较适合作为患者状态建模的起点。

### 3.3 `ed`

`ed` 是急诊数据，适合做早期风险分层或急诊到住院/ICU 的路径分析。  
已经确认的关键表包括：

- `edstays.csv.gz`
- `triage.csv.gz`
- `vitalsign.csv.gz`
- `diagnosis.csv.gz`
- `medrecon.csv.gz`
- `pyxis.csv.gz`

这些表主要记录：

- 急诊停留信息
- 分诊信息
- 急诊生命体征
- 急诊诊断
- 药物相关记录

### 3.4 `note`

`note` 是文本数据，目前确认 zip 内包含：

- `radiology.csv.gz`
- `radiology_detail.csv.gz`
- `discharge.csv.gz`
- `discharge_detail.csv.gz`

这部分适合在后续如果涉及文本、多模态或临床摘要任务时再使用。

## 4. 当前已经确认的数据规模

我已经实际统计过部分核心表的行数：

- `patients`: 364,627
- `admissions`: 546,028
- `icustays`: 94,458
- `edstays`: 425,087

还确认了部分关键主键的唯一值规模：

- `patients.subject_id`: 364,627
- `admissions.hadm_id`: 546,028
- `icustays.stay_id`: 94,458
- `edstays.stay_id`: 425,087

这些数字说明，这个数据集规模较大，后续处理时不能直接粗暴整表读入，需要先选任务、选入口表、选字段。

## 5. 这个数据集最核心的结构是什么

目前最关键的主键有 5 个：

- `subject_id`：患者级 ID
- `hadm_id`：一次住院 ID
- `stay_id`：一次 ICU stay 或 ED stay 的 ID
- `itemid`：某个监测项、化验项或事件项的字典编号
- `icd_code`：诊断或操作编码

### 5.1 最重要的表关系

可以先粗略理解成：

- `patients -> admissions -> icustays`
- `patients -> edstays`

也就是说：

- 一个患者可以有多次住院
- 一次住院可能不进入 ICU，也可能进入 ICU
- 一个患者也可能有急诊停留记录
- 一些急诊记录后续会转成住院

### 5.2 事件表

真正对建模很重要的数据，很多并不在主表里，而是在事件表里，例如：

- `labevents`
- `chartevents`
- `inputevents`
- `vitalsign`

这些表通常带有时间字段，更适合做：

- 时间序列特征构造
- 状态变化分析
- 风险预测
- 患者轨迹建模

### 5.3 字典表

我也确认了两个关键字典表：

- `d_labitems`
  - 用来解释 `labevents.itemid`
- `d_items`
  - 用来解释 ICU 事件表里的 `itemid`

这意味着后续读事件表时，不能只看数值，还必须通过字典表去知道变量真实含义。

## 6. 这个数据集到底能拿来做什么

从数据处理和建模角度，我理解它主要适合做以下事情：

- 患者风险预测
- 多表临床数据清洗与对齐
- 患者时间序列建模
- ICU/急诊患者轨迹建模
- 医疗多模态研究的前期原型验证

结合当前“医疗世界模型 / 围术期世界模型”课题，我的理解是：

### 它适合做的

- 帮助熟悉临床多表结构
- 帮助练习 cohort 构造
- 帮助练习 label 定义
- 帮助做时间对齐和数据管线
- 帮助先做患者状态建模和原型任务

### 它不完全等于的

- 标准围术期术中高频波形数据集
- 完整麻醉全过程专用数据库

更准确地说：

**MIMIC-IV 很适合当前课题前期的数据处理、原型验证和临床时序建模训练，但它不是一个天然就完全贴合“术中世界模型”的专用数据集。**

## 7. 如果要基于它开始做任务，正确思路是什么

这个数据集不是“先选模型”，而是应该先走数据路线：

1. 先选入口表
   - ICU 任务通常从 `icustays` 开始
   - 住院任务通常从 `admissions` 开始
   - 急诊任务通常从 `edstays` 开始
2. 再定义 cohort
   - 研究哪些病人
   - 保留哪些 stay / admission
   - 去掉哪些不符合要求的记录
3. 再定义 label
   - 例如住院死亡
   - ICU 低血压风险
   - 急诊后是否入院或转 ICU
   - 某类并发症代理标签
4. 再抽取特征
   - 静态特征：年龄、性别、种族、诊断等
   - 动态特征：生命体征、化验、输入输出、治疗事件等
5. 再做时间对齐
   - 例如以 ICU 入科为起点
   - 取前 6 小时或前 24 小时数据作为输入
   - 取之后某一时间窗的事件作为预测目标
6. 最后导出训练数据
   - 把原始多表整理成后续模型可以直接使用的样本

## 8. 对当前项目最重要的理解

当前我被分在数据处理组，所以现阶段最重要的事情不是训练模型，而是：

- 认表
- 理清主键关系
- 理解时间字段
- 找核心变量
- 想清楚可以做哪些 cohort
- 想清楚可以定义哪些 label

我目前认为比较现实的起步方向有：

- `ICU cohort`
- `住院 cohort`
- `急诊 cohort`

比较容易先做的 label 有：

- 住院死亡
- ICU 低血压风险
- 急诊后是否入院或转 ICU
- 并发症代理标签

## 9. 一句话总结

这份 MIMIC-IV 数据不是“直接拿来训模型的成品数据”，而是一个大型临床关系型时序数据库。  
对当前项目来说，它最重要的价值是：帮助我们先把医疗数据结构、主键关系、患者轨迹、cohort 构造和 label 设计这条数据主线跑通，为后续更复杂的医疗世界模型研究打基础。
