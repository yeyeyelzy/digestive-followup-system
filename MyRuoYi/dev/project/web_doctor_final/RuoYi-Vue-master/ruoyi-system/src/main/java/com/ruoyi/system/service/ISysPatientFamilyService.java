package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.common.core.domain.entity.SysPatientFamily;
import com.ruoyi.system.domain.Patient;

/**
 * 患者家属关联 Service 接口
 * 
 * @author ruoyi
 */
public interface ISysPatientFamilyService 
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
     * 批量删除患者家属关联
     * 
     * @param ids 需要删除的患者家属关联主键集合
     * @return 结果
     */
    public int deleteSysPatientFamilyByIds(Long[] ids);

    /**
     * 删除患者家属关联信息
     * 
     * @param id 患者家属关联主键
     * @return 结果
     */
    public int deleteSysPatientFamilyById(Long id);

    /**
     * 绑定患者
     */
    public boolean bindPatient(Long familyId, Long patientId, String relationship);
    
    /**
     * 解绑患者
     */
    public boolean unbindPatient(Long familyId, Long patientId);

    /**
     * 家属已绑定的患者列表
     */
    public List<Patient> selectBoundPatientsByFamilyId(Long familyId);
    
    /**
     * 检查是否已绑定
     */
    public boolean isBound(Long familyId, Long patientId);
}
