-- 家属信息表
CREATE TABLE IF NOT EXISTS `sys_family` (
  `family_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '家属ID',
  `family_name` varchar(30) DEFAULT '' COMMENT '家属姓名',
  `phone_number` varchar(11) DEFAULT '' COMMENT '手机号码',
  `password` varchar(100) DEFAULT '' COMMENT '密码',
  `avatar` varchar(255) DEFAULT '' COMMENT '头像路径',
  `gender` char(1) DEFAULT '0' COMMENT '性别（0男 1女 2未知）',
  `age` int(3) DEFAULT NULL COMMENT '年龄',
  `status` char(1) DEFAULT '0' COMMENT '帐号状态（0正常 1停用）',
  `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`family_id`),
  UNIQUE KEY `uk_phone` (`phone_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='家属信息表';

-- 患者-家属绑定关系表
CREATE TABLE IF NOT EXISTS `sys_patient_family` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `family_id` bigint(20) NOT NULL COMMENT '家属ID',
  `patient_id` bigint(20) NOT NULL COMMENT '患者ID',
  `relationship` varchar(50) DEFAULT '' COMMENT '关系（如：父子、夫妻等）',
  `status` char(1) DEFAULT '0' COMMENT '绑定状态（0已绑定 1申请中 2已解绑/拒绝）',
  `create_time` datetime DEFAULT NULL COMMENT '绑定时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_bind` (`family_id`, `patient_id`) -- 防止重复绑定
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='患者家属关联表';