package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.system.domain.ScienceChat;

/**
 * 聊天记录管理Mapper接口
 *
 * @author ruoyi
 * @date 2023-07-11
 */
public interface ScienceChatMapper
{
    /**
     * 查询聊天记录管理
     *
     * @param id 聊天记录管理主键
     * @return 聊天记录管理
     */
    public ScienceChat selectChatById(Long id);

    /**
     * 查询聊天记录管理列表
     *
     * @param chat 聊天记录管理
     * @return 聊天记录管理集合
     */
    public List<ScienceChat> selectChatList(ScienceChat chat);

    /**
     * 新增聊天记录管理
     *
     * @param chat 聊天记录管理
     * @return 结果
     */
    public int insertChat(ScienceChat chat);

    /**
     * 修改聊天记录管理
     *
     * @param chat 聊天记录管理
     * @return 结果
     */
    public int updateChat(ScienceChat chat);

    /**
     * 删除聊天记录管理
     *
     * @param id 聊天记录管理主键
     * @return 结果
     */
    public int deleteChatById(Long id);

    /**
     * 批量删除聊天记录管理
     *
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteChatByIds(Long[] ids);
}
