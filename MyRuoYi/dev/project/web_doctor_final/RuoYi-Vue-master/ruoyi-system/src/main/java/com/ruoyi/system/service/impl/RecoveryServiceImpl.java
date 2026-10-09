package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.RecoveryMapper;
import com.ruoyi.system.domain.Recovery;
import com.ruoyi.system.service.IRecoveryService;

/**
 * 复查管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class RecoveryServiceImpl implements IRecoveryService 
{
    @Autowired
    private RecoveryMapper recoveryMapper;

    /**
     * 查询复查管理
     * 
     * @param recoveryId 复查管理主键
     * @return 复查管理
     */
    @Override
    public Recovery selectRecoveryByRecoveryId(Long recoveryId)
    {
        return recoveryMapper.selectRecoveryByRecoveryId(recoveryId);
    }

    /**
     * 查询复查管理列表
     * 
     * @param recovery 复查管理
     * @return 复查管理
     */
    @Override
    public List<Recovery> selectRecoveryList(Recovery recovery)
    {
        return recoveryMapper.selectRecoveryList(recovery);
    }

    /**
     * 新增复查管理
     * 
     * @param recovery 复查管理
     * @return 结果
     */
    @Override
    public int insertRecovery(Recovery recovery)
    {
        return recoveryMapper.insertRecovery(recovery);
    }

    /**
     * 修改复查管理
     * 
     * @param recovery 复查管理
     * @return 结果
     */
    @Override
    public int updateRecovery(Recovery recovery)
    {
        return recoveryMapper.updateRecovery(recovery);
    }

    /**
     * 批量删除复查管理
     * 
     * @param recoveryIds 需要删除的复查管理主键
     * @return 结果
     */
    @Override
    public int deleteRecoveryByRecoveryIds(Long[] recoveryIds)
    {
        return recoveryMapper.deleteRecoveryByRecoveryIds(recoveryIds);
    }

    /**
     * 删除复查管理信息
     * 
     * @param recoveryId 复查管理主键
     * @return 结果
     */
    @Override
    public int deleteRecoveryByRecoveryId(Long recoveryId)
    {
        return recoveryMapper.deleteRecoveryByRecoveryId(recoveryId);
    }
}
