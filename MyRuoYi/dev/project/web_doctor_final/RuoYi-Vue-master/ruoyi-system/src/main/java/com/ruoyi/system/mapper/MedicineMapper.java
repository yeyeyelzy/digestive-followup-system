package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.system.domain.Medicine;

/**
 * 服药日记管理Mapper接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface MedicineMapper 
{
    /**
     * 查询服药日记管理
     * 
     * @param medicineId 服药日记管理主键
     * @return 服药日记管理
     */
    public Medicine selectMedicineByMedicineId(Long medicineId);

    /**
     * 查询服药日记管理列表
     * 
     * @param medicine 服药日记管理
     * @return 服药日记管理集合
     */
    public List<Medicine> selectMedicineList(Medicine medicine);

    /**
     * 查询服药日记管理列表
     *
     * @param medicine 服药日记管理
     * @return 服药日记管理集合
     */
    public List<Medicine> searchByIdDate(Medicine medicine);

    /**
     * 新增服药日记管理
     * 
     * @param medicine 服药日记管理
     * @return 结果
     */
    public int insertMedicine(Medicine medicine);

    /**
     * 修改服药日记管理
     * 
     * @param medicine 服药日记管理
     * @return 结果
     */
    public int updateMedicine(Medicine medicine);

    /**
     * 修改服药日记管理
     *
     * @param medicine 服药日记管理
     * @return 结果
     */
    public int updateIdDate(Medicine medicine);

    /**
     * 删除服药日记管理
     * 
     * @param medicineId 服药日记管理主键
     * @return 结果
     */
    public int deleteMedicineByMedicineId(Long medicineId);

    /**
     * 批量删除服药日记管理
     * 
     * @param medicineIds 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteMedicineByMedicineIds(Long[] medicineIds);
}
