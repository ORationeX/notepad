package kr.ai.lineosft.projectmanagement.api.project.service;

import kr.ai.lineosft.projectmanagement.api.project.dto.TaskHistoryResponse;
import kr.ai.lineosft.projectmanagement.api.project.dto.TaskRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.TaskResponse;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import kr.ai.lineosft.projectmanagement.domain.member.repository.MemberRepository;
import kr.ai.lineosft.projectmanagement.domain.project.entity.*;
import kr.ai.lineosft.projectmanagement.domain.project.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class TaskService {

    private final TaskRepository taskRepository;
    private final ProjectRepository projectRepository;
    private final MemberRepository memberRepository;
    private final SprintRepository sprintRepository;
    private final PhaseRepository phaseRepository;
    private final TaskHistoryRepository taskHistoryRepository;

    public List<TaskResponse> getTasks(Long projectId) {
        return taskRepository.findByProjectIdWithRelations(projectId).stream()
                .map(TaskResponse::new)
                .collect(Collectors.toList());
    }

    public List<TaskHistoryResponse> getTaskHistories(Long taskId) {
        return taskHistoryRepository.findByTaskIdWithRelations(taskId).stream()
                .map(TaskHistoryResponse::new)
                .collect(Collectors.toList());
    }

    @Transactional
    public TaskResponse createTask(Long projectId, TaskRequest request, Member modifier) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new IllegalArgumentException("프로젝트를 찾을 수 없습니다."));

        Member assignee = null;
        if (request.getAssigneeId() != null) {
            assignee = memberRepository.findById(request.getAssigneeId())
                    .orElseThrow(() -> new IllegalArgumentException("배정할 담당자를 찾을 수 없습니다."));
        }

        Sprint sprint = null;
        if (request.getSprintId() != null) {
            sprint = sprintRepository.findById(request.getSprintId())
                    .orElseThrow(() -> new IllegalArgumentException("스프린트를 찾을 수 없습니다."));
        }

        Phase phase = null;
        if (request.getPhaseId() != null) {
            phase = phaseRepository.findById(request.getPhaseId())
                    .orElseThrow(() -> new IllegalArgumentException("단계를 찾을 수 없습니다."));
        }

        Task task = Task.builder()
                .title(request.getTitle())
                .description(request.getDescription())
                .status(request.getStatus())
                .priority(request.getPriority())
                .startDate(request.getStartDate())
                .endDate(request.getEndDate())
                .progress(request.getProgress())
                .project(project)
                .assignee(assignee)
                .sprint(sprint)
                .phase(phase)
                .build();

        Task savedTask = taskRepository.save(task);

        // 이력 생성
        TaskHistory history = TaskHistory.builder()
                .task(savedTask)
                .fromStatus(null)
                .toStatus(savedTask.getStatus())
                .modifier(modifier)
                .comment("작업 등록됨")
                .build();
        taskHistoryRepository.save(history);

        return new TaskResponse(savedTask);
    }

    @Transactional
    public TaskResponse updateTask(Long taskId, TaskRequest request, Member modifier) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new IllegalArgumentException("태스크를 찾을 수 없습니다."));

        TaskStatus oldStatus = task.getStatus();

        Member assignee = null;
        if (request.getAssigneeId() != null) {
            assignee = memberRepository.findById(request.getAssigneeId())
                    .orElseThrow(() -> new IllegalArgumentException("배정할 담당자를 찾을 수 없습니다."));
        }

        Sprint sprint = null;
        if (request.getSprintId() != null) {
            sprint = sprintRepository.findById(request.getSprintId())
                    .orElseThrow(() -> new IllegalArgumentException("스프린트를 찾을 수 없습니다."));
        }

        Phase phase = null;
        if (request.getPhaseId() != null) {
            phase = phaseRepository.findById(request.getPhaseId())
                    .orElseThrow(() -> new IllegalArgumentException("단계를 찾을 수 없습니다."));
        }

        task.update(
                request.getTitle(),
                request.getDescription(),
                request.getStatus(),
                request.getPriority(),
                request.getStartDate(),
                request.getEndDate(),
                request.getProgress(),
                assignee,
                sprint,
                phase
        );

        if (oldStatus != task.getStatus()) {
            TaskHistory history = TaskHistory.builder()
                    .task(task)
                    .fromStatus(oldStatus)
                    .toStatus(task.getStatus())
                    .modifier(modifier)
                    .comment("상태 변경됨 (수정 모달)")
                    .build();
            taskHistoryRepository.save(history);
        }

        return new TaskResponse(task);
    }

    @Transactional
    public TaskResponse updateTaskStatus(Long taskId, TaskStatus status, Member modifier) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new IllegalArgumentException("태스크를 찾을 수 없습니다."));
        TaskStatus oldStatus = task.getStatus();
        if (oldStatus != status) {
            task.updateStatus(status);
            TaskHistory history = TaskHistory.builder()
                    .task(task)
                    .fromStatus(oldStatus)
                    .toStatus(status)
                    .modifier(modifier)
                    .comment("상태 변경됨 (드래그 앤 드롭)")
                    .build();
            taskHistoryRepository.save(history);
        }
        return new TaskResponse(task);
    }

    @Transactional
    public void deleteTask(Long taskId) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new IllegalArgumentException("태스크를 찾을 수 없습니다."));
        taskRepository.delete(task);
    }

    public List<TaskResponse> getAllTasks() {
        return taskRepository.findAllWithRelations().stream()
                .map(TaskResponse::new)
                .collect(Collectors.toList());
    }
}
