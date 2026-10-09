package com.ruoyi.system.service.impl;

import java.util.List;
import com.ruoyi.common.utils.DateUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.SysPatientFamilyMapper;
import com.ruoyi.common.core.domain.entity.SysPatientFamily;
import com.ruoyi.common.core.domain.entity.PatientUser;
import com.ruoyi.system.service.ISysPatientFamilyService;

/**
 * 患者家属关联 Service 业务层处理
 * 
 * @author ruoyi
 */
@Service
public class SysPatientFamilyServiceImpl implements ISysPatientFamilyService 
{
    @Autowired
    private SysPatientFamilyMapper sysPatientFamilyMapper;

    /**
     * 查询患者家属关联
     * 
     * @param id 患者家属关联主键
     * @return 患者家属关联
     */
    @Override
    public SysPatientFamily selectSysPatientFamilyById(Long id)
    {
        return sysPatientFamilyMapper.selectSysPatientFamilyById(id);
    }

    /**
     * 查询患者家属关联列表
     * 
     * @param sysPatientFamily 患者家属关联
     * @return 患者家属关联
     */
    @Override
    public List<SysPatientFamily> selectSysPatientFamilyList(SysPatientFamily sysPatientFamily)
    {
        return sysPatientFamilyMapper.selectSysPatientFamilyList(sysPatientFamily);
    }

    /**
     * 新增患者家属关联
     * 
     * @param sysPatientFamily 患者家属关联
     * @return 结果
     */
    @Override
    public int insertSysPatientFamily(SysPatientFamily sysPatientFamily)
    {
        sysPatientFamily.setCreateTime(DateUtils.getNowDate());
        return sysPatientFamilyMapper.insertSysPatientFamily(sysPatientFamily);
    }

    /**
     * 修改患者家属关联
     * 
     * @param sysPatientFamily 患者家属关联
     * @return 结果
     */
    @Override
    public int updateSysPatientFamily(SysPatientFamily sysPatientFamily)
    {
        return sysPatientFamilyMapper.updateSysPatientFamily(sysPatientFamily);
    }

    /**
     * 批量删除患者家属关联
     * 
     * @param ids 需要删除的患者家属关联主键
     * @return 结果
     */
    @Override
    public int deleteSysPatientFamilyByIds(Long[] ids)
    {
        return sysPatientFamilyMapper.deleteSysPatientFamilyByIds(ids);
    }

    /**
     * 删除患者家属关联信息
     * 
     * @param id 患者家属关联主键
     * @return 结果
     */
    @Override
    public int deleteSysPatientFamilyById(Long id)
    {
        return sysPatientFamilyMapper.deleteSysPatientFamilyById(id);
    }

    @Override
    public boolean bindPatient(Long familyId, Long patientId, String relationship) {
        if (isBound(familyId, patientId)) {
            return false;
        }
        SysPatientFamily pf = new SysPatientFamily();
        pf.setFamilyId(familyId);
        pf.setPatientId(patientId);
        pf.setRelationship(relationship);
        pf.setStatus("0"); // 假设直接通过
        pf.setCreateTime(DateUtils.getNowDate());
        return insertSysPatientFamily(pf) > 0;
    }

    @Override
    public boolean unbindPatient(Long familyId, Long patientId) {
        SysPatientFamily pf = sysPatientFamilyMapper.selectByFamilyAndPatient(familyId, patientId);
        if (pf != null) {
            return deleteSysPatientFamilyById(pf.getId()) > 0;
        }
        return false;
    }

    @Override
    public List<PatientUser> selectBoundPatientsByFamilyId(Long familyId) {
        return sysPatientFamilyMapper.selectBoundPatientsByFamilyId(familyId);
    }

    @Override
    public boolean isBound(Long familyId, Long patientId) {
        SysPatientFamily pf = sysPatientFamilyMapper.selectByFamilyAndPatient(familyId, patientId);
        return pf != null && "0".equals(pf.getStatus());
    }
}
