package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.BehaviorMapper;
import com.ruoyi.system.domain.Behavior;
import com.ruoyi.system.service.IBehaviorService;

/**
 * 行为日记管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class BehaviorServiceImpl implements IBehaviorService 
{
    @Autowired
    private BehaviorMapper behaviorMapper;

    /**
     * 查询行为日记管理
     * 
     * @param behaviorId 行为日记管理主键
     * @return 行为日记管理
     */
    @Override
    public Behavior selectBehaviorByBehaviorId(Long behaviorId)
    {
        return behaviorMapper.selectBehaviorByBehaviorId(behaviorId);
    }

    /**
     * 查询行为日记管理列表
     * 
     * @param behavior 行为日记管理
     * @return 行为日记管理
     */
    @Override
    public List<Behavior> selectBehaviorList(Behavior behavior)
    {
        return behaviorMapper.selectBehaviorList(behavior);
    }


    /**
     * 新增行为日记管理
     *
     * @param behavior 行为日记管理
     * @return 结果
     */
    @Override
    public List<Behavior> searchByIdDate(Behavior behavior){
        return behaviorMapper.searchByIdDate(behavior);
    }


    /**
     * 新增行为日记管理
     * 
     * @param behavior 行为日记管理
     * @return 结果
     */
    @Override
    public int insertBehavior(Behavior behavior)
    {
        return behaviorMapper.insertBehavior(behavior);
    }

    /**
     * 修改行为日记管理
     * 
     * @param behavior 行为日记管理
     * @return 结果
     */
    @Override
    public int updateBehavior(Behavior behavior)
    {
        return behaviorMapper.updateBehavior(behavior);
    }

    /**
     * 根据id日期修改行为日记管理
     *
     * @param behavior 行为日记管理
     * @return 结果
     */
    @Override
    public int updateIdDate(Behavior behavior)
    {
        return behaviorMapper.updateIdDate(behavior);
    }

    /**
     * 批量删除行为日记管理
     * 
     * @param behaviorIds 需要删除的行为日记管理主键
     * @return 结果
     */
    @Override
    public int deleteBehaviorByBehaviorIds(Long[] behaviorIds)
    {
        return behaviorMapper.deleteBehaviorByBehaviorIds(behaviorIds);
    }

    /**
     * 删除行为日记管理信息
     * 
     * @param behaviorId 行为日记管理主键
     * @return 结果
     */
    @Override
    public int deleteBehaviorByBehaviorId(Long behaviorId)
    {
        return behaviorMapper.deleteBehaviorByBehaviorId(behaviorId);
    }
}
