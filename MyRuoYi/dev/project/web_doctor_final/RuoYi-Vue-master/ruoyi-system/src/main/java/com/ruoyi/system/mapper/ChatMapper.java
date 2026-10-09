package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.system.domain.Chat;

/**
 * 聊天记录管理Mapper接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface ChatMapper 
{
    /**
     * 查询聊天记录管理
     * 
     * @param id 聊天记录管理主键
     * @return 聊天记录管理
     */
    public Chat selectChatById(Long id);

    /**
     * 查询聊天记录管理列表
     * 
     * @param chat 聊天记录管理
     * @return 聊天记录管理集合
     */
    public List<Chat> selectChatList(Chat chat);

    /**
     * 新增聊天记录管理
     * 
     * @param chat 聊天记录管理
     * @return 结果
     */
    public int insertChat(Chat chat);

    /**
     * 修改聊天记录管理
     * 
     * @param chat 聊天记录管理
     * @return 结果
     */
    public int updateChat(Chat chat);

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
