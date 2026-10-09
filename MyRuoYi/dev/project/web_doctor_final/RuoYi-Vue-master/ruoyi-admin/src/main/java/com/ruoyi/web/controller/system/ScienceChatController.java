package com.ruoyi.web.controller.system;

import java.util.List;
import javax.annotation.Resource;
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
import com.ruoyi.system.domain.ScienceChat;
import com.ruoyi.system.service.IScienceChatService;
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
@RequestMapping("/system/science_chat")
public class ScienceChatController extends BaseController
{
    @Resource
    private IScienceChatService sciChatService;

    /**
     * 查询聊天记录管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:science_chat:list')")
    @GetMapping("/list")
    public TableDataInfo list(ScienceChat chat)
    {
        startPage();
        List<ScienceChat> list = sciChatService.selectChatList(chat);
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
    @PreAuthorize("@ss.hasPermi('system:science_chat:export')")
    @Log(title = "聊天记录管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, ScienceChat chat)
    {
        List<ScienceChat> list = sciChatService.selectChatList(chat);
        ExcelUtil<ScienceChat> util = new ExcelUtil<ScienceChat>(ScienceChat.class);
        util.exportExcel(response, list, "科普聊天记录管理数据");
    }

    /**
     * 获取聊天记录管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:science_chat:query')")
    @GetMapping(value = "/{id}")
    public AjaxResult getInfo(@PathVariable("id") Long id)
    {
        return success(sciChatService.selectChatById(id));
    }

    /**
     * 新增聊天记录管理
     */
    @PreAuthorize("@ss.hasPermi('system:science_chat:add')")
    @Log(title = "科普聊天记录管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody ScienceChat chat)
    {
        return toAjax(sciChatService.insertChat(chat));
    }

    /**
     * 修改聊天记录管理
     */
    @PreAuthorize("@ss.hasPermi('system:science_chat:edit')")
    @Log(title = "科普聊天记录管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody ScienceChat chat)
    {
        return toAjax(sciChatService.updateChat(chat));
    }

    /**
     * 删除聊天记录管理
     */
    @PreAuthorize("@ss.hasPermi('system:science_chat:remove')")
    @Log(title = "聊天记录管理", businessType = BusinessType.DELETE)
    @DeleteMapping("/{ids}")
    public AjaxResult remove(@PathVariable Long[] ids)
    {
        return toAjax(sciChatService.deleteChatByIds(ids));
    }
}
