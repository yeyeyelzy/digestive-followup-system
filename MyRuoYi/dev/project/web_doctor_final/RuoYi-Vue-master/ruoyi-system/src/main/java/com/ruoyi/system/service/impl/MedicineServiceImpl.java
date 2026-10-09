package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.MedicineMapper;
import com.ruoyi.system.domain.Medicine;
import com.ruoyi.system.service.IMedicineService;

/**
 * 服药日记管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class MedicineServiceImpl implements IMedicineService 
{
    @Autowired
    private MedicineMapper medicineMapper;

    /**
     * 查询服药日记管理
     * 
     * @param medicineId 服药日记管理主键
     * @return 服药日记管理
     */
    @Override
    public Medicine selectMedicineByMedicineId(Long medicineId)
    {
        return medicineMapper.selectMedicineByMedicineId(medicineId);
    }

    /**
     * 查询服药日记管理列表
     * 
     * @param medicine 服药日记管理
     * @return 服药日记管理
     */
    @Override
    public List<Medicine> selectMedicineList(Medicine medicine)
    {
        return medicineMapper.selectMedicineList(medicine);
    }

    /**
     * 查询服药日记管理列表
     *
     * @param medicine 服药日记管理
     * @return 服药日记管理
     */
    @Override
    public List<Medicine> searchByIdDate(Medicine medicine)
    {
        return medicineMapper.searchByIdDate(medicine);
    }

    /**
     * 新增服药日记管理
     * 
     * @param medicine 服药日记管理
     * @return 结果
     */
    @Override
    public int insertMedicine(Medicine medicine)
    {
        return medicineMapper.insertMedicine(medicine);
    }

    /**
     * 修改服药日记管理
     * 
     * @param medicine 服药日记管理
     * @return 结果
     */
    @Override
    public int updateMedicine(Medicine medicine)
    {
        return medicineMapper.updateMedicine(medicine);
    }

    /**
     * 修改服药日记管理
     *
     * @param medicine 服药日记管理
     * @return 结果
     */
    @Override
    public int updateIdDate(Medicine medicine)
    {
        return medicineMapper.updateIdDate(medicine);
    }

    /**
     * 批量删除服药日记管理
     * 
     * @param medicineIds 需要删除的服药日记管理主键
     * @return 结果
     */
    @Override
    public int deleteMedicineByMedicineIds(Long[] medicineIds)
    {
        return medicineMapper.deleteMedicineByMedicineIds(medicineIds);
    }

    /**
     * 删除服药日记管理信息
     * 
     * @param medicineId 服药日记管理主键
     * @return 结果
     */
    @Override
    public int deleteMedicineByMedicineId(Long medicineId)
    {
        return medicineMapper.deleteMedicineByMedicineId(medicineId);
    }
}
