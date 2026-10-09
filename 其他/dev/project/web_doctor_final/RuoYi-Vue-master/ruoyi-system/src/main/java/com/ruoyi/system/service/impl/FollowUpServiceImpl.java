package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.FollowUpMapper;
import com.ruoyi.system.domain.FollowUp;
import com.ruoyi.system.service.IFollowUpService;

/**
 * 随访记录管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class FollowUpServiceImpl implements IFollowUpService 
{
    @Autowired
    private FollowUpMapper followUpMapper;

    /**
     * 查询随访记录管理
     * 
     * @param followUpId 随访记录管理主键
     * @return 随访记录管理
     */
    @Override
    public FollowUp selectFollowUpByFollowUpId(Long followUpId)
    {
        return followUpMapper.selectFollowUpByFollowUpId(followUpId);
    }

    /**
     * 查询随访记录管理列表
     * 
     * @param followUp 随访记录管理
     * @return 随访记录管理
     */
    @Override
    public List<FollowUp> selectFollowUpList(FollowUp followUp)
    {
        return followUpMapper.selectFollowUpList(followUp);
    }

    /**
     * 新增随访记录管理
     * 
     * @param followUp 随访记录管理
     * @return 结果
     */
    @Override
    public int insertFollowUp(FollowUp followUp)
    {
        return followUpMapper.insertFollowUp(followUp);
    }

    /**
     * 修改随访记录管理
     * 
     * @param followUp 随访记录管理
     * @return 结果
     */
    @Override
    public int updateFollowUp(FollowUp followUp)
    {
        return followUpMapper.updateFollowUp(followUp);
    }

    /**
     * 批量删除随访记录管理
     * 
     * @param followUpIds 需要删除的随访记录管理主键
     * @return 结果
     */
    @Override
    public int deleteFollowUpByFollowUpIds(Long[] followUpIds)
    {
        return followUpMapper.deleteFollowUpByFollowUpIds(followUpIds);
    }

    /**
     * 删除随访记录管理信息
     * 
     * @param followUpId 随访记录管理主键
     * @return 结果
     */
    @Override
    public int deleteFollowUpByFollowUpId(Long followUpId)
    {
        return followUpMapper.deleteFollowUpByFollowUpId(followUpId);
    }
}
