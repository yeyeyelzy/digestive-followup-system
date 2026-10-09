package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.ChatMapper;
import com.ruoyi.system.domain.Chat;
import com.ruoyi.system.service.IChatService;

/**
 * 聊天记录管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class ChatServiceImpl implements IChatService 
{
    @Autowired
    private ChatMapper chatMapper;

    /**
     * 查询聊天记录管理
     * 
     * @param id 聊天记录管理主键
     * @return 聊天记录管理
     */
    @Override
    public Chat selectChatById(Long id)
    {
        return chatMapper.selectChatById(id);
    }

    /**
     * 查询聊天记录管理列表
     * 
     * @param chat 聊天记录管理
     * @return 聊天记录管理
     */
    @Override
    public List<Chat> selectChatList(Chat chat)
    {
        return chatMapper.selectChatList(chat);
    }

    /**
     * 新增聊天记录管理
     * 
     * @param chat 聊天记录管理
     * @return 结果
     */
    @Override
    public int insertChat(Chat chat)
    {
        return chatMapper.insertChat(chat);
    }

    /**
     * 修改聊天记录管理
     * 
     * @param chat 聊天记录管理
     * @return 结果
     */
    @Override
    public int updateChat(Chat chat)
    {
        return chatMapper.updateChat(chat);
    }

    /**
     * 批量删除聊天记录管理
     * 
     * @param ids 需要删除的聊天记录管理主键
     * @return 结果
     */
    @Override
    public int deleteChatByIds(Long[] ids)
    {
        return chatMapper.deleteChatByIds(ids);
    }

    /**
     * 删除聊天记录管理信息
     * 
     * @param id 聊天记录管理主键
     * @return 结果
     */
    @Override
    public int deleteChatById(Long id)
    {
        return chatMapper.deleteChatById(id);
    }
}
