-- 修复任务（2026-03-20）
-- 1) 删除 patient_id=16 的患者（按任务要求）
-- 2) 依据 patient_user.phonenumber 回填 patient.phone_number 的空值

START TRANSACTION;

DELETE FROM patient WHERE patient_id = 16;

UPDATE patient p
INNER JOIN patient_user pu ON pu.patient_id = p.patient_id
SET p.phone_number = pu.phonenumber
WHERE (p.phone_number IS NULL OR p.phone_number = '')
  AND pu.phonenumber IS NOT NULL
  AND pu.phonenumber <> '';

COMMIT;
