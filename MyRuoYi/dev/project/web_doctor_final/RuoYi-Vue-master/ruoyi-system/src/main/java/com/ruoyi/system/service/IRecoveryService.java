package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.Recovery;

/**
 * 复查管理Service接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface IRecoveryService 
{
    /**
     * 查询复查管理
     * 
     * @param recoveryId 复查管理主键
     * @return 复查管理
     */
    public Recovery selectRecoveryByRecoveryId(Long recoveryId);

    /**
     * 查询复查管理列表
     * 
     * @param recovery 复查管理
     * @return 复查管理集合
     */
    public List<Recovery> selectRecoveryList(Recovery recovery);

    /**
     * 新增复查管理
     * 
     * @param recovery 复查管理
     * @return 结果
     */
    public int insertRecovery(Recovery recovery);

    /**
     * 修改复查管理
     * 
     * @param recovery 复查管理
     * @return 结果
     */
    public int updateRecovery(Recovery recovery);

    /**
     * 批量删除复查管理
     * 
     * @param recoveryIds 需要删除的复查管理主键集合
     * @return 结果
     */
    public int deleteRecoveryByRecoveryIds(Long[] recoveryIds);

    /**
     * 删除复查管理信息
     * 
     * @param recoveryId 复查管理主键
     * @return 结果
     */
    public int deleteRecoveryByRecoveryId(Long recoveryId);
}
