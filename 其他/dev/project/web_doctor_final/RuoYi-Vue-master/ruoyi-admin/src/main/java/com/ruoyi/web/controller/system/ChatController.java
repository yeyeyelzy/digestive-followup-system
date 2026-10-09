package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.system.service.ISysUserService;
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

import static com.ruoyi.framework.datasource.DynamicDataSourceContextHolder.log;

/**
 * 聊天记录管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
//@Anonymous
@RequestMapping("/system/chat")
public class ChatController extends BaseController
{
    @Autowired
    private IChatService chatService;

    @Autowired
    private ISysUserService sysUserService;

    /**
     * 查询聊天记录管理列表
     */
//    @PreAuthorize("@ss.hasPermi('system:chat:list')")
    @GetMapping("/list")
    public TableDataInfo list(Chat chat)
    {
        // 移除 startPage()，聊天记录不应该分页，或使用特定的分页方法
        // startPage();

        List<Chat> list = chatService.selectChatList(chat);

        // 由于前端小程序期望的是 { rows: [], total: X } 这种格式，我们继续使用 getDataTable
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
//    @PreAuthorize("@ss.hasPermi('system:chat:add')")
//    @Log(title = "聊天记录管理", businessType = BusinessType.INSERT)
//    @PostMapping
//    public AjaxResult add(@RequestBody Chat chat)
//    {
//        return toAjax(chatService.insertChat(chat));
//    }

    // 【【【 新增：发送消息接口逻辑修正（POST /system/chat）】】】
    // 你的前端 sendOut 方法调用的是 POST /chat，对应的是 @PostMapping
    @PostMapping
    @Log(title = "聊天记录管理", businessType = BusinessType.INSERT)
    public AjaxResult add(@RequestBody Chat chat)
    {
        // 如果你的数据库表 chat 的 time 字段是自动填充的，可以省略这一步。
        // 如果不是，建议在这里设置时间
        // chat.setTime(new Date());

        // **关键点：你的前端在 chat.js 中已经传入了 patientId, patientName, doctorId, doctorName, direction, content**
        // 所以这里直接插入即可
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
