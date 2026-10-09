package com.ruoyi.system.service.impl;

import java.util.List;
import com.ruoyi.common.utils.DateUtils;
import com.ruoyi.common.utils.SecurityUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.SysFamilyMapper;
import com.ruoyi.common.core.domain.entity.SysFamily;
import com.ruoyi.system.service.ISysFamilyService;

/**
 * 家属信息 Service 业务层处理
 * 
 * @author ruoyi
 */
@Service
public class SysFamilyServiceImpl implements ISysFamilyService 
{
    @Autowired
    private SysFamilyMapper sysFamilyMapper;

    /**
     * 查询家属信息
     * 
     * @param familyId 家属信息主键
     * @return 家属信息
     */
    @Override
    public SysFamily selectSysFamilyByFamilyId(Long familyId)
    {
        return sysFamilyMapper.selectSysFamilyByFamilyId(familyId);
    }

    /**
     * 查询家属信息列表
     * 
     * @param sysFamily 家属信息
     * @return 家属信息
     */
    @Override
    public List<SysFamily> selectSysFamilyList(SysFamily sysFamily)
    {
        return sysFamilyMapper.selectSysFamilyList(sysFamily);
    }

    /**
     * 新增家属信息
     * 
     * @param sysFamily 家属信息
     * @return 结果
     */
    @Override
    public int insertSysFamily(SysFamily sysFamily)
    {
        sysFamily.setCreateTime(DateUtils.getNowDate());
        return sysFamilyMapper.insertSysFamily(sysFamily);
    }

    /**
     * 修改家属信息
     * 
     * @param sysFamily 家属信息
     * @return 结果
     */
    @Override
    public int updateSysFamily(SysFamily sysFamily)
    {
        sysFamily.setUpdateTime(DateUtils.getNowDate());
        return sysFamilyMapper.updateSysFamily(sysFamily);
    }

    /**
     * 批量删除家属信息
     * 
     * @param familyIds 需要删除的家属信息主键
     * @return 结果
     */
    @Override
    public int deleteSysFamilyByFamilyIds(Long[] familyIds)
    {
        return sysFamilyMapper.deleteSysFamilyByFamilyIds(familyIds);
    }

    /**
     * 删除家属信息信息
     * 
     * @param familyId 家属信息主键
     * @return 结果
     */
    @Override
    public int deleteSysFamilyByFamilyId(Long familyId)
    {
        return sysFamilyMapper.deleteSysFamilyByFamilyId(familyId);
    }

    @Override
    public SysFamily selectSysFamilyByPhoneNumber(String phoneNumber) {
        return sysFamilyMapper.selectSysFamilyByPhoneNumber(phoneNumber);
    }

    @Override
    public boolean registerFamily(SysFamily sysFamily) {
        SysFamily exist = selectSysFamilyByPhoneNumber(sysFamily.getPhoneNumber());
        if (exist != null) {
            return false;
        }
        sysFamily.setPassword(SecurityUtils.encryptPassword(sysFamily.getPassword()));
        sysFamily.setCreateTime(DateUtils.getNowDate());
        return insertSysFamily(sysFamily) > 0;
    }
}
