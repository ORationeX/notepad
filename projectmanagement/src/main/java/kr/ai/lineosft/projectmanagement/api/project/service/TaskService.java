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
    private final RequirementRepository requirementRepository;
    private final RequirementHistoryRepository requirementHistoryRepository;

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

        Requirement requirement = null;
        if (request.getRequirementId() != null) {
            requirement = requirementRepository.findById(request.getRequirementId())
                    .orElseThrow(() -> new IllegalArgumentException("요구사항을 찾을 수 없습니다."));
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
                .requirement(requirement)
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

        // 요구사항 상태 자동 전환 트리거
        if (requirement != null) {
            syncRequirementStatus(requirement, modifier);
        }

        return new TaskResponse(savedTask);
    }

    @Transactional
    public TaskResponse updateTask(Long taskId, TaskRequest request, Member modifier) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new IllegalArgumentException("태스크를 찾을 수 없습니다."));

        TaskStatus oldStatus = task.getStatus();
        Requirement oldRequirement = task.getRequirement();

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

        Requirement requirement = null;
        if (request.getRequirementId() != null) {
            requirement = requirementRepository.findById(request.getRequirementId())
                    .orElseThrow(() -> new IllegalArgumentException("요구사항을 찾을 수 없습니다."));
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
                phase,
                requirement
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

        // 요구사항 상태 자동 전환 트리거
        if (oldRequirement != null) {
            syncRequirementStatus(oldRequirement, modifier);
        }
        if (requirement != null && !requirement.equals(oldRequirement)) {
            syncRequirementStatus(requirement, modifier);
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

            // 요구사항 상태 자동 전환 트리거
            if (task.getRequirement() != null) {
                syncRequirementStatus(task.getRequirement(), modifier);
            }
        }
        return new TaskResponse(task);
    }

    @Transactional
    public void deleteTask(Long taskId) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new IllegalArgumentException("태스크를 찾을 수 없습니다."));
        Requirement requirement = task.getRequirement();
        taskRepository.delete(task);

        // 요구사항 상태 자동 전환 트리거
        if (requirement != null) {
            syncRequirementStatus(requirement, null);
        }
    }

    public List<TaskResponse> getAllTasks() {
        return taskRepository.findAllWithRelations().stream()
                .map(TaskResponse::new)
                .collect(Collectors.toList());
    }

    private void syncRequirementStatus(Requirement requirement, Member modifier) {
        if (requirement == null) return;
        List<Task> tasks = taskRepository.findByRequirementId(requirement.getId());
        if (tasks.isEmpty()) return;

        boolean anyInProgress = false;
        boolean allDone = true;

        for (Task t : tasks) {
            if (t.getStatus() == TaskStatus.IN_PROGRESS) {
                anyInProgress = true;
            }
            if (t.getStatus() != TaskStatus.DONE) {
                allDone = false;
            }
        }

        RequirementStatus oldStatus = requirement.getStatus();
        RequirementStatus newStatus = null;

        if (allDone) {
            newStatus = RequirementStatus.COMPLETED;
        } else if (anyInProgress) {
            newStatus = RequirementStatus.DEVELOPING;
        }

        if (newStatus != null && oldStatus != newStatus) {
            requirement.updateStatus(newStatus);
            requirementRepository.save(requirement);

            RequirementHistory history = RequirementHistory.builder()
                    .requirement(requirement)
                    .title(requirement.getTitle())
                    .description(requirement.getDescription())
                    .category(requirement.getCategory())
                    .priority(requirement.getPriority())
                    .status(requirement.getStatus())
                    .progress(requirement.getProgress())
                    .requestedBy(requirement.getRequestedBy())
                    .domainName(requirement.getDomainName())
                    .modifier(modifier)
                    .comment("태스크 상태 변경에 의한 상태 자동 전환 (" + oldStatus.getDescription() + " -> " + newStatus.getDescription() + ")")
                    .build();
            requirementHistoryRepository.save(history);
        }
    }
}
