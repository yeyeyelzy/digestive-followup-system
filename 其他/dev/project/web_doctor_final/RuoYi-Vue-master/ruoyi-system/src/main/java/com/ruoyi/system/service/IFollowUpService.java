package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.FollowUp;

/**
 * 随访记录管理Service接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface IFollowUpService 
{
    /**
     * 查询随访记录管理
     * 
     * @param followUpId 随访记录管理主键
     * @return 随访记录管理
     */
    public FollowUp selectFollowUpByFollowUpId(Long followUpId);

    /**
     * 查询随访记录管理列表
     * 
     * @param followUp 随访记录管理
     * @return 随访记录管理集合
     */
    public List<FollowUp> selectFollowUpList(FollowUp followUp);

    /**
     * 新增随访记录管理
     * 
     * @param followUp 随访记录管理
     * @return 结果
     */
    public int insertFollowUp(FollowUp followUp);

    /**
     * 修改随访记录管理
     * 
     * @param followUp 随访记录管理
     * @return 结果
     */
    public int updateFollowUp(FollowUp followUp);

    /**
     * 批量删除随访记录管理
     * 
     * @param followUpIds 需要删除的随访记录管理主键集合
     * @return 结果
     */
    public int deleteFollowUpByFollowUpIds(Long[] followUpIds);

    /**
     * 删除随访记录管理信息
     * 
     * @param followUpId 随访记录管理主键
     * @return 结果
     */
    public int deleteFollowUpByFollowUpId(Long followUpId);
}
