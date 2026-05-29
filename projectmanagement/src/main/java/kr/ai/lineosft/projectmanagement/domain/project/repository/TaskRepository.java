package kr.ai.lineosft.projectmanagement.domain.project.repository;

import kr.ai.lineosft.projectmanagement.domain.project.entity.Task;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface TaskRepository extends JpaRepository<Task, Long> {
    @Query("SELECT t FROM Task t LEFT JOIN FETCH t.assignee LEFT JOIN FETCH t.sprint LEFT JOIN FETCH t.phase WHERE t.project.id = :projectId ORDER BY t.createdAt DESC")
    List<Task> findByProjectIdWithRelations(@Param("projectId") Long projectId);

    @Query("SELECT t FROM Task t JOIN FETCH t.project LEFT JOIN FETCH t.assignee LEFT JOIN FETCH t.sprint LEFT JOIN FETCH t.phase ORDER BY t.startDate ASC, t.createdAt DESC")
    List<Task> findAllWithRelations();
}
