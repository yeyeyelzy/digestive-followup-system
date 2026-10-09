package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.annotation.Log;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.enums.BusinessType;
import com.ruoyi.system.domain.Chat;
import com.ruoyi.system.service.IChatService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 聊天记录管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@Anonymous
@RequestMapping("/system/chat")
public class ChatController extends BaseController
{
    @Autowired
    private IChatService chatService;

    /**
     * 查询聊天记录管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:chat:list')")
    @GetMapping("/list")
    public TableDataInfo list(Chat chat)
    {
        startPage();
        List<Chat> list = chatService.selectChatList(chat);
        return getDataTable(list);
    }

//    @GetMapping("/testa")
//    public TableDataInfo a(Chat chat)
//    {
////        startPage();
////        List<Chat> list = chatService.selectChatList(chat);
//        return getDataTable(list);
//    }

    /**
     * 导出聊天记录管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:chat:export')")
    @Log(title = "聊天记录管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Chat chat)
    {
        List<Chat> list = chatService.selectChatList(chat);
        ExcelUtil<Chat> util = new ExcelUtil<Chat>(Chat.class);
        util.exportExcel(response, list, "聊天记录管理数据");
    }

    /**
     * 获取聊天记录管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:chat:query')")
    @GetMapping(value = "/{id}")
    public AjaxResult getInfo(@PathVariable("id") Long id)
    {
        return success(chatService.selectChatById(id));
    }

    /**
     * 新增聊天记录管理
     */
    @PreAuthorize("@ss.hasPermi('system:chat:add')")
    @Log(title = "聊天记录管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Chat chat)
    {
        return toAjax(chatService.insertChat(chat));
    }

    /**
     * 修改聊天记录管理
     */
    @PreAuthorize("@ss.hasPermi('system:chat:edit')")
    @Log(title = "聊天记录管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Chat chat)
    {
        return toAjax(chatService.updateChat(chat));
    }

    /**
     * 删除聊天记录管理
     */
    @PreAuthorize("@ss.hasPermi('system:chat:remove')")
    @Log(title = "聊天记录管理", businessType = BusinessType.DELETE)
	@DeleteMapping("/{ids}")
    public AjaxResult remove(@PathVariable Long[] ids)
    {
        return toAjax(chatService.deleteChatByIds(ids));
    }
}
