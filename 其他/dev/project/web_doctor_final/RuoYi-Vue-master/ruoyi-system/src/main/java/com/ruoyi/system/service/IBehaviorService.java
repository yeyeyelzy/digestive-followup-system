package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.Behavior;

/**
 * 行为日记管理Service接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface IBehaviorService 
{
    /**
     * 查询行为日记管理
     * 
     * @param behaviorId 行为日记管理主键
     * @return 行为日记管理
     */
    public Behavior selectBehaviorByBehaviorId(Long behaviorId);

    /**
     * 查询行为日记管理列表
     * 
     * @param behavior 行为日记管理
     * @return 行为日记管理集合
     */
    public List<Behavior> selectBehaviorList(Behavior behavior);

    /**
     * 新增行为日记管理
     * 
     * @param behavior 行为日记管理
     * @return 结果
     */
    public List<Behavior> searchByIdDate(Behavior behavior);

    public int insertBehavior(Behavior behavior);

    /**
     * 修改行为日记管理
     * 
     * @param behavior 行为日记管理
     * @return 结果
     */
    public int updateBehavior(Behavior behavior);

    /**
     * 根据id日期修改行为日记管理
     *
     * @param behavior 行为日记管理
     * @return 结果
     */
    public int updateIdDate(Behavior behavior);

    /**
     * 批量删除行为日记管理
     * 
     * @param behaviorIds 需要删除的行为日记管理主键集合
     * @return 结果
     */
    public int deleteBehaviorByBehaviorIds(Long[] behaviorIds);

    /**
     * 删除行为日记管理信息
     * 
     * @param behaviorId 行为日记管理主键
     * @return 结果
     */
    public int deleteBehaviorByBehaviorId(Long behaviorId);
}
