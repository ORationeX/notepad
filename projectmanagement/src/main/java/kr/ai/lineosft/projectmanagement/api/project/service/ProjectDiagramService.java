package kr.ai.lineosft.projectmanagement.api.project.service;

import kr.ai.lineosft.projectmanagement.api.project.dto.ProjectDiagramRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.ProjectDiagramResponse;
import kr.ai.lineosft.projectmanagement.domain.project.entity.ProjectDiagram;
import kr.ai.lineosft.projectmanagement.domain.project.entity.Requirement;
import kr.ai.lineosft.projectmanagement.domain.project.entity.Task;
import kr.ai.lineosft.projectmanagement.domain.project.repository.ProjectDiagramRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.RequirementRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ProjectDiagramService {

    private final ProjectDiagramRepository projectDiagramRepository;
    private final RequirementRepository requirementRepository;
    private final TaskRepository taskRepository;

    public List<ProjectDiagramResponse> getDiagramsByRequirement(Long requirementId) {
        return projectDiagramRepository.findByRequirementIdWithRelations(requirementId).stream()
                .map(ProjectDiagramResponse::new)
                .collect(Collectors.toList());
    }

    public ProjectDiagramResponse getDiagram(Long id) {
        ProjectDiagram diagram = projectDiagramRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("다이어그램을 찾을 수 없습니다. ID: " + id));
        return new ProjectDiagramResponse(diagram);
    }

    @Transactional
    public ProjectDiagramResponse createDiagram(Long requirementId, ProjectDiagramRequest request) {
        Requirement requirement = requirementRepository.findById(requirementId)
                .orElseThrow(() -> new IllegalArgumentException("요구사항을 찾을 수 없습니다. ID: " + requirementId));

        Task task = null;
        if (request.getLastModifiedByTaskId() != null) {
            task = taskRepository.findById(request.getLastModifiedByTaskId())
                    .orElseThrow(() -> new IllegalArgumentException("태스크를 찾을 수 없습니다. ID: " + request.getLastModifiedByTaskId()));
        }

        ProjectDiagram diagram = ProjectDiagram.builder()
                .title(request.getTitle())
                .mermaidCode(request.getMermaidCode())
                .requirement(requirement)
                .lastModifiedByTask(task)
                .build();

        ProjectDiagram saved = projectDiagramRepository.save(diagram);
        return new ProjectDiagramResponse(saved);
    }

    @Transactional
    public ProjectDiagramResponse updateDiagram(Long id, ProjectDiagramRequest request) {
        ProjectDiagram diagram = projectDiagramRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("다이어그램을 찾을 수 없습니다. ID: " + id));

        Task task = null;
        if (request.getLastModifiedByTaskId() != null) {
            task = taskRepository.findById(request.getLastModifiedByTaskId())
                    .orElseThrow(() -> new IllegalArgumentException("태스크를 찾을 수 없습니다. ID: " + request.getLastModifiedByTaskId()));
        }

        diagram.update(request.getTitle(), request.getMermaidCode(), task);
        return new ProjectDiagramResponse(diagram);
    }

    @Transactional
    public void deleteDiagram(Long id) {
        ProjectDiagram diagram = projectDiagramRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("다이어그램을 찾을 수 없습니다. ID: " + id));
        projectDiagramRepository.delete(diagram);
    }
}
