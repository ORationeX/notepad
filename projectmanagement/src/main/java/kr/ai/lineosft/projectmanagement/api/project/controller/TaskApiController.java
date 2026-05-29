package kr.ai.lineosft.projectmanagement.api.project.controller;

import jakarta.validation.Valid;
import kr.ai.lineosft.projectmanagement.api.project.dto.TaskHistoryResponse;
import kr.ai.lineosft.projectmanagement.api.project.dto.TaskRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.TaskResponse;
import kr.ai.lineosft.projectmanagement.api.project.service.TaskService;
import kr.ai.lineosft.projectmanagement.domain.project.entity.TaskStatus;
import kr.ai.lineosft.projectmanagement.global.security.CustomUserDetails;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class TaskApiController {

    private final TaskService taskService;

    @GetMapping("/api/projects/{projectId}/tasks")
    public ResponseEntity<List<TaskResponse>> getTasks(@PathVariable Long projectId) {
        return ResponseEntity.ok(taskService.getTasks(projectId));
    }

    @GetMapping("/api/tasks")
    public ResponseEntity<List<TaskResponse>> getAllTasks() {
        return ResponseEntity.ok(taskService.getAllTasks());
    }

    @PostMapping("/api/projects/{projectId}/tasks")
    public ResponseEntity<TaskResponse> createTask(
            @PathVariable Long projectId,
            @Valid @RequestBody TaskRequest request,
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        TaskResponse createdTask = taskService.createTask(projectId, request, userDetails.getMember());
        return ResponseEntity.status(HttpStatus.CREATED).body(createdTask);
    }

    @PutMapping("/api/tasks/{taskId}")
    public ResponseEntity<TaskResponse> updateTask(
            @PathVariable Long taskId,
            @Valid @RequestBody TaskRequest request,
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        return ResponseEntity.ok(taskService.updateTask(taskId, request, userDetails.getMember()));
    }

    @PatchMapping("/api/tasks/{taskId}/status")
    public ResponseEntity<TaskResponse> updateTaskStatus(
            @PathVariable Long taskId,
            @RequestParam TaskStatus status,
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        return ResponseEntity.ok(taskService.updateTaskStatus(taskId, status, userDetails.getMember()));
    }

    @GetMapping("/api/tasks/{taskId}/histories")
    public ResponseEntity<List<TaskHistoryResponse>> getTaskHistories(@PathVariable Long taskId) {
        return ResponseEntity.ok(taskService.getTaskHistories(taskId));
    }

    @DeleteMapping("/api/tasks/{taskId}")
    public ResponseEntity<Void> deleteTask(@PathVariable Long taskId) {
        taskService.deleteTask(taskId);
        return ResponseEntity.noContent().build();
    }
}
