package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.ScienceChatMapper;
import com.ruoyi.system.domain.ScienceChat;
import com.ruoyi.system.service.IScienceChatService;

/**
 * 聊天记录管理Service业务层处理
 *
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class ScienceChatServiceImpl implements IScienceChatService
{
    @Autowired
    private ScienceChatMapper scienceChatMapper;

    /**
     * 查询聊天记录管理
     *
     * @param id 聊天记录管理主键
     * @return 聊天记录管理
     */
    @Override
    public ScienceChat selectChatById(Long id)
    {
        return scienceChatMapper.selectChatById(id);
    }

    /**
     * 查询聊天记录管理列表
     *
     * @param chat 聊天记录管理
     * @return 聊天记录管理
     */
    @Override
    public List<ScienceChat> selectChatList(ScienceChat chat)
    {
        return scienceChatMapper.selectChatList(chat);
    }

    /**
     * 新增聊天记录管理
     *
     * @param chat 聊天记录管理
     * @return 结果
     */
    @Override
    public int insertChat(ScienceChat chat)
    {
        return scienceChatMapper.insertChat(chat);
    }

    /**
     * 修改聊天记录管理
     *
     * @param chat 聊天记录管理
     * @return 结果
     */
    @Override
    public int updateChat(ScienceChat chat)
    {
        return scienceChatMapper.updateChat(chat);
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
        return scienceChatMapper.deleteChatByIds(ids);
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
        return scienceChatMapper.deleteChatById(id);
    }
}
