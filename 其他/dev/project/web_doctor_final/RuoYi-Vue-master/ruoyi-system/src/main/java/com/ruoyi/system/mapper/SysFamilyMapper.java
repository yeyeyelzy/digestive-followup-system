package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.common.core.domain.entity.SysFamily;

/**
 * 家属信息 Mapper 接口
 * 
 * @author ruoyi
 */
public interface SysFamilyMapper 
{
    /**
     * 查询家属信息
     * 
     * @param familyId 家属信息主键
     * @return 家属信息
     */
    public SysFamily selectSysFamilyByFamilyId(Long familyId);

    /**
     * 查询家属信息列表
     * 
     * @param sysFamily 家属信息
     * @return 家属信息集合
     */
    public List<SysFamily> selectSysFamilyList(SysFamily sysFamily);

    /**
     * 新增家属信息
     * 
     * @param sysFamily 家属信息
     * @return 结果
     */
    public int insertSysFamily(SysFamily sysFamily);

    /**
     * 修改家属信息
     * 
     * @param sysFamily 家属信息
     * @return 结果
     */
    public int updateSysFamily(SysFamily sysFamily);

    /**
     * 删除家属信息
     * 
     * @param familyId 家属信息主键
     * @return 结果
     */
    public int deleteSysFamilyByFamilyId(Long familyId);

    /**
     * 批量删除家属信息
     * 
     * @param familyIds 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteSysFamilyByFamilyIds(Long[] familyIds);

    /**
     * 根据手机号查询家属信息
     * @param phoneNumber 手机号码
     * @return 家属信息
     */
    public SysFamily selectSysFamilyByPhoneNumber(String phoneNumber);
}
