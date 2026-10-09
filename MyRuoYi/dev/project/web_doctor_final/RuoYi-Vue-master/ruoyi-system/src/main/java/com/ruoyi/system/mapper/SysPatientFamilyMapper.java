package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.common.core.domain.entity.SysPatientFamily;
import com.ruoyi.system.domain.Patient;
import org.apache.ibatis.annotations.Param;

/**
 * 患者家属关联 Mapper 接口
 * 
 * @author ruoyi
 */
public interface SysPatientFamilyMapper 
{
    /**
     * 查询患者家属关联
     * 
     * @param id 患者家属关联主键
     * @return 患者家属关联
     */
    public SysPatientFamily selectSysPatientFamilyById(Long id);

    /**
     * 查询患者家属关联列表
     * 
     * @param sysPatientFamily 患者家属关联
     * @return 患者家属关联集合
     */
    public List<SysPatientFamily> selectSysPatientFamilyList(SysPatientFamily sysPatientFamily);

    /**
     * 新增患者家属关联
     * 
     * @param sysPatientFamily 患者家属关联
     * @return 结果
     */
    public int insertSysPatientFamily(SysPatientFamily sysPatientFamily);

    /**
     * 修改患者家属关联
     * 
     * @param sysPatientFamily 患者家属关联
     * @return 结果
     */
    public int updateSysPatientFamily(SysPatientFamily sysPatientFamily);

    /**
     * 删除患者家属关联
     * 
     * @param id 患者家属关联主键
     * @return 结果
     */
    public int deleteSysPatientFamilyById(Long id);

    /**
     * 批量删除患者家属关联
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteSysPatientFamilyByIds(Long[] ids);

    /**
     * 根据 familyId 和 patientId 查询关联信息
     */
    public SysPatientFamily selectByFamilyAndPatient(@Param("familyId") Long familyId, @Param("patientId") Long patientId);

    /**
     * 根据 familyId 查询关联的患者列表 (需要关联查询 patient 表)
     */
    public List<Patient> selectBoundPatientsByFamilyId(Long familyId);
}
